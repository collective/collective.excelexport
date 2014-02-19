# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.excelexport.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of collective.excelexport into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.excelexport is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.excelexport'))

    def test_uninstall(self):
        """Test if collective.excelexport is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.excelexport'])
        self.assertFalse(self.installer.isProductInstalled('collective.excelexport'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveExcelexportLayer is registered."""
        from collective.excelexport.interfaces import ICollectiveExcelexportLayer
        from plone.browserlayer import utils
        self.assertIn(ICollectiveExcelexportLayer, utils.registered_layers())
