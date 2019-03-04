# -*- coding: utf-8 -*-
"""Base module for unittesting."""

import unittest

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

import collective.excelexport
import pkg_resources
from plone import api

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_PA_CONTENTTYPES = False
else:
    HAS_PA_CONTENTTYPES = True


class CollectiveExcelexportLayer(PloneWithPackageLayer):

    def setUpZope(self, *args, **kwargs):
        """Prepare Zope instance"""
        super(CollectiveExcelexportLayer, self).setUpZope(*args, **kwargs)
        if HAS_PA_CONTENTTYPES:
            import plone.app.contenttypes
            self.loadZCML(package=plone.app.contenttypes)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        super(CollectiveExcelexportLayer, self).setUpPloneSite(portal)

        # Plone 5 support
        if HAS_PA_CONTENTTYPES:
            self.applyProfile(portal, 'plone.app.contenttypes:default')

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        api.content.create(
            container=portal,
            type='Folder',
            id='folder',
        )


FIXTURE = CollectiveExcelexportLayer(
    zcml_package=collective.excelexport,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.excelexport:testing',
    name="FIXTURE",
)

INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="INTEGRATION"
)

FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,),
    name="FUNCTIONAL"
)


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL
