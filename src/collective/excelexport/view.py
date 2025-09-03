from collective.excelexport.interfaces import IDataSource
from collective.excelexport.interfaces import IStyles
from copy import copy
from csv import writer as csvwriter
from DateTime import DateTime
from io import BytesIO
from io import StringIO
from plone.base.utils import safe_text
from Products.Five.browser import BrowserView
from xlwt import CompoundDoc
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.interface.interfaces import ComponentLookupError

import datetime
import xlwt


class BaseExport(BrowserView):
    def _format_render(self, render):
        """Common formatting to unicode"""
        if isinstance(render, Message):
            render = translate(render, context=self.request)
        elif isinstance(render, str):
            pass
        elif render is None:
            render = ""
        elif isinstance(render, datetime.datetime):
            render = safe_text(render.strftime("%Y/%m/%d %H:%M"))
        elif isinstance(render, (DateTime, datetime.date)):
            try:
                render = safe_text(render.strftime("%Y/%m/%d"))
            except ValueError:
                # when date < 1900
                render = safe_text(render)
        elif not isinstance(render, str):
            render = safe_text(str(render))
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
        return string_buffer


class ExcelExport(BaseExport):
    """Excel export view"""

    mimetype = "application/vnd.ms-excel"
    extension = "xls"
    encoding = "windows-1252"

    def write_sheet(self, sheet, sheetinfo, styles):
        # values
        for rownum, obj in enumerate(sheetinfo["objects"]):
            for exportablenum, exportable in enumerate(sheetinfo["exportables"]):
                try:
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
            sheet.write(0, 0, "", styles.content)

        return xldoc

    def get_data_buffer(self, sheetsinfo, policy=""):
        string_buffer = BytesIO()
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

    def __call__(self):
        string_buffer = super(ExcelExport, self).__call__()
        return string_buffer.getvalue()


class CSVExport(BaseExport):
    mimetype = "text/csv"
    extension = "csv"
    encoding = "windows-1252"

    def _format_render(self, render):
        render = super(CSVExport, self)._format_render(render)
        if not isinstance(render, str):
            render = str(render)
        return render

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

    def __call__(self):
        string_buffer = super(CSVExport, self).__call__()
        data = string_buffer.getvalue()
        return data.encode(self.encoding, errors="replace")
