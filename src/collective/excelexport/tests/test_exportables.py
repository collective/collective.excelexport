# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.component import adapts
from zope.component import getGlobalSiteManager
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface.declarations import implements

from collective.excelexport.exportables.dexterityfields import ChoiceFieldRenderer
from collective.excelexport.exportables.dexterityfields import IFieldValueGetter
from collective.excelexport.testing import IntegrationTestCase


class IFakeInterface(Interface):
    """ Fake interface """


class FakeValueGetter(object):
    adapts(IFakeInterface)
    implements(IFieldValueGetter)

    def __init__(self, context):
        self.context = context

    def get(self, field):
        return field.value


class TestExportables(IntegrationTestCase):
    """Test exportables."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(factory=FakeValueGetter)
        alsoProvides(self.folder, IFakeInterface)

    def test_ChoiceFieldRenderer(self):
        # with values param: vocabulary but no title
        field = schema.Choice(title=u'Test', values=['ok', 'nok'])
        field.value = 'nok'
        renderer = ChoiceFieldRenderer(field, self.folder, self.portal.REQUEST)
        self.assertEqual(renderer.render_value(renderer.context), 'nok')
        # with values: but empty value (or no value)
        field.value = ''
        self.assertEqual(renderer.render_value(renderer.context), '')
        # with values: but unfound value in vocabulary
        field.value = 'missing'
        self.assertEqual(renderer.render_value(renderer.context), 'missing')
        # with vocabulary param
        devs = SimpleVocabulary([SimpleTerm(value=u'sgeulette', title=u'Stephan Geulette')])
        field = schema.Choice(title=u'Test', vocabulary=devs)
        field.value = 'sgeulette'
        renderer = ChoiceFieldRenderer(field, self.folder, self.portal.REQUEST)
        self.assertEqual(renderer.render_value(renderer.context), 'Stephan Geulette')
        # with source param

        def mysource(obj):
            return devs
        alsoProvides(mysource, IContextSourceBinder)
        field = schema.Choice(title=u'Test', source=mysource)
        field.value = 'sgeulette'
        renderer = ChoiceFieldRenderer(field, self.folder, self.portal.REQUEST)
        self.assertEqual(renderer.render_value(renderer.context), 'Stephan Geulette')
