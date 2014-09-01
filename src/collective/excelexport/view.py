from csv import writer as csvwriter
from copy import copy
from StringIO import StringIO

import xlwt
from xlwt import CompoundDoc

from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from Products.Five.browser import BrowserView

from collective.excelexport.interfaces import IDataSource, IStyles


class BaseExport(BrowserView):

    def set_headers(self, datasource):
        self.request.response.setHeader('Cache-Control', 'no-cache')
        self.request.response.setHeader('Pragma', 'no-cache')
        self.request.response.setHeader(
            'Content-type', '%s;charset=%s' % (self.mimetype, self.encoding))
        filename = datasource.get_filename()
        if not filename.endswith(self.extension):  # false only for bbb
            filename = "%s.%s" % (datasource.get_filename(),
                                  self.extension)

        self.request.response.setHeader(
            'Content-disposition',
            'attachment; filename="%s"' % filename
            )


class ExcelExport(BaseExport):
    """Excel export view
    """
    mimetype = 'application/vnd.ms-excel'
    extension = 'xls'
    encoding = 'windows-1252'

    def _format_render(self, render):
        """Common formatting
        """
        if isinstance(render, Message):
            render = translate(render, context=self.request)
        elif isinstance(render, str):
            render = unicode(render)

        return render

    def write_sheet(self, sheet, sheetinfo, styles):
        # headers
        for exportablenum, exportable in enumerate(sheetinfo['exportables']):
            render = exportable.render_header()
            render = self._format_render(render)
            sheet.write(0, exportablenum, render, styles.headers)

        # values
        for rownum, obj in enumerate(sheetinfo['objects']):
            for exportablenum, exportable in enumerate(sheetinfo['exportables']):
                render = exportable.render_value(obj)
                render = self._format_render(render)
                sheet.write(rownum + 1, exportablenum, render,
                            exportable.render_style(obj, copy(styles.content)))

    def get_xldoc(self, sheetsinfo, styles):
        xldoc = xlwt.Workbook(encoding='utf-8')
        empty_doc = True
        for sheetnum, sheetinfo in enumerate(sheetsinfo):
            if len(sheetinfo['exportables']) == 0:
                continue

            # sheet
            empty_doc = False
            title = self._format_render(sheetinfo['title'])
            sheet_title = title.replace("'", " ").replace(':', '-').replace('/', '-')[:31]

            try:
                sheet = xldoc.add_sheet(sheet_title)
            except Exception:
                sheet = xldoc.add_sheet(sheet_title + ' ' + str(sheetnum))

            self.write_sheet(sheet, sheetinfo, styles)

        if empty_doc:
            # empty doc
            sheet = xldoc.add_sheet('sheet 1')
            sheet.write(0, 0, u"", styles.content)

        return xldoc

    def __call__(self):
        string_buffer = StringIO()

        # get all values to display, one value by sheet
        policy = self.request.get('excelexport.policy', '')
        datasource = getMultiAdapter((self.context, self.request),
                               interface=IDataSource, name=policy)
        self.set_headers(datasource)
        sheetsinfo = datasource.get_sheets_data()

        try:
            styles = getMultiAdapter((self.context, self.request),
                                     interface=IStyles, name=policy)
        except ComponentLookupError:
            styles = getMultiAdapter((self.context, self.request),
                                     interface=IStyles)

        xldoc = self.get_xldoc(sheetsinfo, styles)
        doc = CompoundDoc.XlsDoc()
        data = xldoc.get_biff_data()
        doc.save(string_buffer, data)
        return string_buffer.getvalue()


class CSVExport(BaseExport):

    mimetype = 'application/vnd.ms-excel'
    extension = 'csv'
    encoding = 'windows-1252'

    def _format_render(self, render):
        """Common formatting
        """
        if render is None:
            render = u""
        elif isinstance(render, Message):
            render = translate(render, context=self.request)
        elif not isinstance(render, unicode):
            render = unicode(render)

        return render.encode(encoding=self.encoding)

    def __call__(self):
        string_buffer = StringIO()
        csvhandler = csvwriter(string_buffer, dialect='excel', delimiter=';')
        policy = self.request.get('excelexport.policy', '')
        datasource = getMultiAdapter((self.context, self.request),
                               interface=IDataSource, name=policy)
        self.set_headers(datasource)
        sheetsinfo = datasource.get_sheets_data()

        sheetsinfo = [s for s in sheetsinfo if len(s['exportables']) > 0]
        for sheetnum, sheetinfo in enumerate(sheetsinfo):
            # title if several tables
            if len(sheetsinfo) >= 2:
                if sheetnum != 0:
                    csvhandler.writerow([''])
                sheet_title = self._format_render(sheetinfo['title'])
                csvhandler.writerow([sheet_title])

            # headers
            headerline = []
            for exportable in sheetinfo['exportables']:
                render = exportable.render_header()
                render = self._format_render(render)
                headerline.append(render)

            csvhandler.writerow(headerline)

            # values
            for obj in sheetinfo['objects']:
                valuesline = []
                for exportable in sheetinfo['exportables']:
                    render = exportable.render_value(obj)
                    render = self._format_render(render)
                    valuesline.append(render)

                if any((v != '' for v in valuesline)):
                    # write row only if there is one not empty line
                    csvhandler.writerow(valuesline)

        return string_buffer.getvalue()