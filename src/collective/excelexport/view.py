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


class ExcelExport(BrowserView):
    """Excel export view
    """
    sheet = NotImplemented

    def set_headers(self, datasource):
        self.request.response.setHeader('Cache-Control', 'no-cache')
        self.request.response.setHeader('Pragma', 'no-cache')
        self.request.response.setHeader(
            'Content-type', 'application/vnd.ms-excel;charset=windows-1252')
        self.request.response.setHeader(
            'Content-disposition',
            'attachment; filename="%s"' % datasource.get_filename()
            )

    def write_sheet(self, sheet, sheetinfo, styles):
        # headers
        for exportablenum, exportable in enumerate(sheetinfo['exportables']):
            render = exportable.render_header()
            if isinstance(render, Message):
                render = translate(render, context=self.request)
            sheet.write(0, exportablenum, render, styles.headers)

        # values
        for rownum, obj in enumerate(sheetinfo['objects']):
            for exportablenum, exportable in enumerate(sheetinfo['exportables']):
                render = exportable.render_value(obj)
                if isinstance(render, Message):
                    render = translate(render, context=self.request)
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
            sheet_title = sheetinfo['title'].replace("'", " ").replace(':', '-').replace('/', '-')[:31]

            try:
                sheet = xldoc.add_sheet(sheet_title)
            except Exception:
                sheet = xldoc.add_sheet(sheet_title + ' ' + str(sheetnum))

            self.write_sheet(sheet, sheetinfo, styles)

        if empty_doc:
            # empty doc
            sheet = xldoc.add_sheet('sheet 1')
            sheet.write(0, 0, "", styles.content)

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
