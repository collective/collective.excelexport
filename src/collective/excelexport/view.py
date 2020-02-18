import datetime

try:
    from StringIO import StringIO  ## for Python 2
except ImportError:
    from io import StringIO  ## for Python 3
from copy import copy
from csv import writer as csvwriter

import xlwt
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from collective.excelexport.interfaces import IDataSource, IStyles
from xlwt import CompoundDoc
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.i18n import translate
from zope.i18nmessageid.message import Message


class BaseExport(BrowserView):
    def _format_render(self, render):
        """Common formatting to unicode
        """
        if isinstance(render, Message):
            render = translate(render, context=self.request)
        elif isinstance(render, unicode):
            pass
        elif render is None:
            render = u""
        elif isinstance(render, str):
            render = safe_unicode(render)
        elif isinstance(render, datetime.datetime):
            render = safe_unicode(render.strftime("%Y/%m/%d %H:%M"))
        elif isinstance(render, (DateTime, datetime.date)):
            try:
                render = safe_unicode(render.strftime("%Y/%m/%d"))
            except ValueError:
                # when date < 1900
                render = safe_unicode(render)
        elif not isinstance(render, unicode):
            render = safe_unicode(str(render))

        return render

    def set_headers(self, datasource):
        self.request.response.setHeader("Cache-Control", "no-cache")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.setHeader(
            "Content-type", "%s;charset=%s" % (self.mimetype, self.encoding)
        )
        filename = datasource.get_filename()
        if not filename.endswith(self.extension):  # false only for bbb
            filename = "%s.%s" % (datasource.get_filename(), self.extension)

        self.request.response.setHeader(
            "Content-disposition", 'attachment; filename="%s"' % filename
        )

    def get_data_buffer(self, sheetsinfo, policy=None):
        raise NotImplementedError

    def __call__(self):
        # get all values to display, one value by sheet
        policy = self.request.get("excelexport.policy", "")
        datasource = getMultiAdapter(
            (self.context, self.request), interface=IDataSource, name=policy
        )
        self.set_headers(datasource)
        sheetsinfo = datasource.get_sheets_data()
        string_buffer = self.get_data_buffer(sheetsinfo, policy=policy)
        return string_buffer.getvalue()


class ExcelExport(BaseExport):
    """Excel export view
    """

    mimetype = "application/vnd.ms-excel"
    extension = "xls"
    encoding = "windows-1252"

    def write_sheet(self, sheet, sheetinfo, styles):
        # values
        for rownum, obj in enumerate(sheetinfo["objects"]):
            for exportablenum, exportable in enumerate(sheetinfo["exportables"]):
                try:
                    # dexterity
                    bound_obj = exportable.field.bind(obj).context
                except AttributeError:
                    bound_obj = obj

                style = exportable.render_style(bound_obj, copy(styles.content))
                style_headers = getattr(style, "headers", styles.headers)
                style_content = getattr(style, "content", style)
                if rownum == 0:
                    # headers
                    render = exportable.render_header()
                    render = self._format_render(render)
                    sheet.write(0, exportablenum, render, style_headers)

                render = exportable.render_value(bound_obj)
                render = self._format_render(render)
                sheet.write(rownum + 1, exportablenum, render, style_content)

    def get_xldoc(self, sheetsinfo, styles):
        xldoc = xlwt.Workbook(encoding="utf-8")
        empty_doc = True
        for sheetnum, sheetinfo in enumerate(sheetsinfo):
            if len(sheetinfo["exportables"]) == 0:
                continue

            # sheet
            empty_doc = False
            title = self._format_render(sheetinfo["title"])
            sheet_title = (
                title.replace("'", " ").replace(":", "-").replace("/", "-")[:31]
            )

            try:
                sheet = xldoc.add_sheet(sheet_title)
            except Exception:
                sheet = xldoc.add_sheet(sheet_title + " " + str(sheetnum))

            self.write_sheet(sheet, sheetinfo, styles)

        if empty_doc:
            # empty doc
            sheet = xldoc.add_sheet("sheet 1")
            sheet.write(0, 0, u"", styles.content)

        return xldoc

    def get_data_buffer(self, sheetsinfo, policy=""):
        string_buffer = StringIO()
        try:
            styles = getMultiAdapter(
                (self.context, self.request), interface=IStyles, name=policy
            )
        except ComponentLookupError:
            styles = getMultiAdapter((self.context, self.request), interface=IStyles)

        xldoc = self.get_xldoc(sheetsinfo, styles)
        doc = CompoundDoc.XlsDoc()
        data = xldoc.get_biff_data()
        doc.save(string_buffer, data)
        return string_buffer


class CSVExport(BaseExport):
    mimetype = "text/csv"
    extension = "csv"
    encoding = "windows-1252"

    def _format_render(self, render):
        render = super(CSVExport, self)._format_render(render)
        try:
            return render.encode(encoding=self.encoding)
        except UnicodeEncodeError:
            # try default encoding
            return render.encode(encoding="utf-8")

    def get_data_buffer(self, sheetsinfo, policy=None):
        string_buffer = StringIO()
        csvhandler = csvwriter(string_buffer, dialect="excel", delimiter=";")
        sheetsinfo = [s for s in sheetsinfo if len(s["exportables"]) > 0]
        for sheetnum, sheetinfo in enumerate(sheetsinfo):
            # title if several tables
            if len(sheetsinfo) >= 2:
                if sheetnum != 0:
                    csvhandler.writerow([""])
                sheet_title = self._format_render(sheetinfo["title"])
                csvhandler.writerow([sheet_title])

            # headers
            headerline = []
            for exportable in sheetinfo["exportables"]:
                render = exportable.render_header()
                render = self._format_render(render)
                headerline.append(render)

            csvhandler.writerow(headerline)

            # values
            for obj in sheetinfo["objects"]:
                valuesline = []
                for exportable in sheetinfo["exportables"]:
                    bound_obj = (
                        exportable.field.bind(obj).context
                        if hasattr(exportable, "field")
                        else obj
                    )
                    render = exportable.render_value(bound_obj)
                    render = self._format_render(render)
                    valuesline.append(render)

                if any((v != "" for v in valuesline)):
                    # write row only if there is one not empty line
                    csvhandler.writerow(valuesline)

        return string_buffer
