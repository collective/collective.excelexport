from copy import copy
from datetime import datetime
from StringIO import StringIO

import xlwt
from xlwt import CompoundDoc

from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from Products.Five.browser import BrowserView

from collective.excelexport.interfaces import IDataSource, IStyles


class ExcelExport(BrowserView):
    """Excel export view
    """
    sheet = NotImplemented

    def get_filename(self):
        return "%s-%s" % (
                datetime.now().strftime("%d-%m-%Y"), self.__name__)

    def __call__(self):
        self.request.response.setHeader(
            'Content-type', 'application/vnd.ms-excel;charset=windows-1252')
        self.request.response.setHeader(
            'Content-disposition',
            'attachment; filename="%s"' % self.get_filename()
            )
        self.request.RESPONSE.setHeader('Cache-Control', 'no-cache')
        self.request.RESPONSE.setHeader('Pragma', 'no-cache')

        string_buffer = StringIO()
        xlDoc = xlwt.Workbook(encoding='utf-8')

        # get all values to display, one value by sheet
        policy = self.request.get('excelexport.policy', '')
        sheetsinfo = getMultiAdapter((self.context, self.request),
                                     interface=IDataSource, name=policy).get_sheets_data()

        try:
            styles = getMultiAdapter((self.context, self.request),
                                     interface=IStyles, name=policy)
        except ComponentLookupError:
            styles = getMultiAdapter((self.context, self.request),
                                     interface=IStyles)

        for sheetnum, sheetinfo in enumerate(sheetsinfo):
            sheet_title = sheetinfo['title'].replace("'", " ").replace(':', '-').replace('/', '-')[:31]

            try:
                sheet = xlDoc.add_sheet(sheet_title)
            except Exception:
                sheet = xlDoc.add_sheet(sheet_title + ' ' + str(sheetnum))

            for exportablenum, exportable in enumerate(sheetinfo['exportables']):
                sheet.write(0, exportablenum,
                            exportable.render_header(),
                            copy(styles.headers))

            for rownum, obj in enumerate(sheetinfo['objects']):
                for exportablenum, exportable in enumerate(sheetinfo['exportables']):
                    sheet.write(rownum + 1, exportablenum,
                                exportable.render_value(obj),
                                exportable.render_style(obj, copy(styles.content)))

        doc = CompoundDoc.XlsDoc()
        data = xlDoc.get_biff_data()
        doc.save(string_buffer, data)

        return string_buffer.getvalue()
