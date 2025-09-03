# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from collective.excelexport.datasources.base import BaseContentsDataSource
from collective.excelexport.datasources.folder import FolderContentsDataSource
from collective.excelexport.testing import IntegrationTestCase
from csv import reader as csvreader
from plone import api
from plone.app.testing.helpers import login
from plone.app.testing.interfaces import TEST_USER_NAME
from plone.namedfile.file import NamedImage
from Products.CMFPlone.utils import get_installer
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import datetime
import os
import tempfile


TEST_IMAGE = os.path.join(os.path.dirname(__file__), "logoplone.png")


class TestExcelExport(IntegrationTestCase):
    """Test installation of collective.excelexport into Plone."""

    def _get_generated_filepath(self, output, suffix):
        generated_path = tempfile.mktemp(suffix=suffix)
        mode = "wb" if isinstance(output, (bytes, bytearray)) else "w"
        with open(generated_path, mode) as generated_file:
            generated_file.write(output)
        generated_file.close()
        return generated_path

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        intids = getUtility(IIntIds)

        login(self.portal, TEST_USER_NAME)
        container = api.content.create(self.portal, type="Folder", id="container")
        self.content1 = api.content.create(
            container,
            type="member",
            id="johndoe",
            title="John Doe",
            birth_date=datetime.date(1980, 7, 24),
            amount=100,
            subscription="silver",
            languages=("en", "fr"),
            biography="Longtemps, je me suis couché de bonne heure",
            photo=NamedImage(
                open(TEST_IMAGE, "rb").read(),
                contentType="image/png",
                filename="logoplone.png",
            ),
        )
        self.content2 = api.content.create(
            container,
            type="member",
            id="johnsmith",
            title="John Smith",
            birth_date=datetime.date(1981, 7, 24),
            amount=100,
            languages=("en", "es"),
            photo=None,
            biography="""Je forme une entreprise qui n'eut jamais d'exemple
et dont l’exécution n'aura point d’imitateur.
Je veux montrer à mes semblables un homme dans toute la vérité de la nature ; et cet homme
ce sera moi.""",
            relatedItems=[RelationValue(intids.getId(self.content1))],
        )

    def test_product_installed(self):
        """Test if collective.excelexport is installed."""
        self.assertTrue(self.installer.is_product_installed("collective.excelexport"))

    def test_uninstall(self):
        """Test if collective.excelexport is cleanly uninstalled."""
        self.installer.uninstall_product("collective.excelexport")
        self.assertFalse(self.installer.is_product_installed("collective.excelexport"))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveExcelexportLayer is registered."""
        from collective.excelexport.interfaces import ICollectiveExcelexportLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveExcelexportLayer, utils.registered_layers())

    def test_export(self):
        self.content3 = api.content.create(
            self.portal.container,
            type="member2",
            id="jfk",
            title="John Fitzgerald Kennedy",
        )
        import xlrd

        output = self.portal.container.unrestrictedTraverse(
            "@@collective.excelexport"
        )()
        generated_path = self._get_generated_filepath(output, "test.xls")
        sheets = xlrd.open_workbook(generated_path)
        self.assertEqual(sheets.sheet_names(), ["member", "member 2"])
        sheet = sheets.sheet_by_name("member")
        headers_row = sheet.row_values(0)
        self.assertEqual(
            headers_row,
            [
                "Name",
                "Biography",
                "Birth date",
                "subscription",
                "amount",
                "Languages",
                "Photo",
                "Related Items",
            ],
        )
        row1 = sheet.row_values(1)
        self.assertEqual(
            row1,
            [
                "John Doe",
                "Longtemps, je me suis couch\xe9 de bonne heure",
                "1980/07/24",
                "silver",
                "100",
                "English\nFran\xe7ais",
                "logoplone.png",
                "",
            ],
        )
        row2 = sheet.row_values(2)
        self.assertEqual(
            row2,
            [
                "John Smith",
                "Je forme une entreprise qui n'eut jamais d'exem...",
                "1981/07/24",
                "",
                "100",
                "English\nEspa\xf1ol",
                "",
                "John Doe",
            ],
        )
        os.remove(generated_path)
        sheet2 = sheets.sheet_by_name("member 2")
        sheet2_row1 = sheet2.row_values(1)
        self.assertEqual(
            sheet2_row1, ["John Fitzgerald Kennedy", "", "", "", "", "", "", ""]
        )

    def test_csv_export(self):
        output = self.portal.container.unrestrictedTraverse(
            "@@collective.excelexportcsv"
        )()
        generated_path = self._get_generated_filepath(output, "test.csv")
        lines = csvreader(
            open(generated_path, "r", encoding="windows-1252", newline=""),
            dialect="excel",
            delimiter=";",
        )
        headers_row = next(lines)
        self.assertEqual(
            headers_row,
            [
                "Name",
                "Biography",
                "Birth date",
                "subscription",
                "amount",
                "Languages",
                "Photo",
                "Related Items",
            ],
        )
        row1 = next(lines)
        self.assertEqual(
            row1,
            [
                "John Doe",
                "Longtemps, je me suis couch\xe9 de bonne heure",
                "1980/07/24",
                "silver",
                "100",
                "English\nFran\xe7ais",
                "logoplone.png",
                "",
            ],
        )
        row2 = next(lines)
        self.assertEqual(
            row2,
            [
                "John Smith",
                "Je forme une entreprise qui n'eut jamais d'exem...",
                "1981/07/24",
                "",
                "100",
                "English\nEspa\xf1ol",
                "",
                "John Doe",
            ],
        )
        os.remove(generated_path)

    def test_searchpolicy_export(self):
        import xlrd

        self.portal.REQUEST.form["excelexport.policy"] = "excelexport.search"
        self.portal.REQUEST.form["getId"] = "johndoe"
        output = self.portal.unrestrictedTraverse("@@collective.excelexport")()
        generated_path = self._get_generated_filepath(output, "test.xls")
        sheets = xlrd.open_workbook(generated_path)
        self.assertEqual(sheets.sheet_names(), ["member"])
        sheet = sheets.sheet_by_name("member")
        headers_row = sheet.row_values(0)
        self.assertEqual(
            headers_row,
            [
                "Name",
                "Biography",
                "Birth date",
                "subscription",
                "amount",
                "Languages",
                "Photo",
                "Related Items",
            ],
        )
        row1 = sheet.row_values(1)
        self.assertEqual(
            row1,
            [
                "John Doe",
                "Longtemps, je me suis couch\xe9 de bonne heure",
                "1980/07/24",
                "silver",
                "100",
                "English\nFran\xe7ais",
                "logoplone.png",
                "",
            ],
        )
        with self.assertRaises(IndexError):
            sheet.row_values(2)

        os.remove(generated_path)

    def test_empty_doc(self):
        import xlrd

        self.portal.REQUEST.form["excelexport.policy"] = "excelexport.search"
        self.portal.REQUEST.form["getId"] = "blabla"
        output = self.portal.unrestrictedTraverse("@@collective.excelexport")()
        generated_path = self._get_generated_filepath(output, "test.xls")
        sheets = xlrd.open_workbook(generated_path)
        self.assertEqual(sheets.sheet_names(), ["sheet 1"])
        del self.portal.REQUEST.form["getId"]

    def test_filter_factories(self):
        source = FolderContentsDataSource(self.portal.container, self.portal.REQUEST)
        data = source.get_sheets_data()
        self.assertEqual(len(data[0]["exportables"]), 8)

        class TestContentsDataSource(FolderContentsDataSource):

            def filter_exportables(self, exportables):
                """You can filter exportables here"""
                return [
                    exportable
                    for exportable in exportables
                    if exportable.field.__name__ != "relatedItems"
                ]

        source = TestContentsDataSource(self.portal.container, self.portal.REQUEST)
        data = source.get_sheets_data()
        self.assertEqual(len(data[0]["exportables"]), 7)

        class TestContentsDataSource2(FolderContentsDataSource):
            excluded_exportables = [
                "biography",
                "birth_date",
                "amount",
                "photo",
            ]

        source = TestContentsDataSource2(self.portal.container, self.portal.REQUEST)
        data = source.get_sheets_data()
        self.assertEqual(len(data[0]["exportables"]), 4)

    def test_default_excluded_exportables_record(self):
        api.portal.set_registry_record(
            name="collective.excelexport.excluded_exportables", value=[]
        )
        source = FolderContentsDataSource(self.portal.container, self.portal.REQUEST)
        data = source.get_sheets_data()
        self.assertEqual(len(data[0]["exportables"]), 8)

        api.portal.set_registry_record(
            name="collective.excelexport.excluded_exportables", value=["title"]
        )

        source = FolderContentsDataSource(self.portal.container, self.portal.REQUEST)
        data = source.get_sheets_data()
        self.assertEqual(len(data[0]["exportables"]), 7)

    def test_order_exportables(self):
        class TestContentsDataSource(FolderContentsDataSource):
            exportables_order = [
                "biography",
                "birth_date",
                "amount",
                "photo",
            ]

        source = TestContentsDataSource(self.portal.container, self.portal.REQUEST)
        data = source.get_sheets_data()
        exportables = data[0]["exportables"]
        self.assertEqual(len(data[0]["exportables"]), 8)
        self.assertEqual(exportables[0].field.__name__, "biography")
        self.assertEqual(exportables[1].field.__name__, "birth_date")
        self.assertEqual(exportables[2].field.__name__, "amount")
        self.assertEqual(exportables[3].field.__name__, "photo")

    def test_order_similar_exportables(self):
        class DummyExportable(object):
            pass

        class DummyExportable2(object):
            pass

        class DummyExportable3(object):
            pass

        class TestContentsDataSource(BaseContentsDataSource):
            exportables_order = [DummyExportable.__name__, DummyExportable2.__name__]

        source = TestContentsDataSource(None, None)

        exportables = source.sort_exportables(
            [
                DummyExportable3(),
                DummyExportable(),
                DummyExportable2(),
                DummyExportable(),
                DummyExportable2(),
            ]
        )
        self.assertEqual(len(exportables), 5)
        self.assertEqual(exportables[0].__class__, DummyExportable)
        self.assertEqual(exportables[1].__class__, DummyExportable)
        self.assertEqual(exportables[2].__class__, DummyExportable2)
        self.assertEqual(exportables[3].__class__, DummyExportable2)
        self.assertEqual(exportables[4].__class__, DummyExportable3)
