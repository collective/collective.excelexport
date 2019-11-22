# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.excelexport.exportables.dexterityfields import ChoiceFieldRenderer
from collective.excelexport.exportables.dexterityfields import IFieldValueGetter
from collective.excelexport.exportables.dexterityfields import get_exportable_for_fieldname
from collective.excelexport.interfaces import IExportable
from collective.excelexport.testing import IntegrationTestCase
from plone import api
from zope import schema
from zope.component import adapts
from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface.declarations import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class IFakeInterface(Interface):
    """ Fake interface """


@implementer(IFieldValueGetter)
class FakeValueGetter(object):
    adapts(IFakeInterface)

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

    def test_ChoiceFieldRenderer_render_collection_entry_unicode(self):
        # render_collection_entry with non unicode vocabulary value
        devs = SimpleVocabulary([SimpleTerm(value=u'sgeulette', title='Stéphan Geulette')])
        field = schema.Choice(title=u'Test', vocabulary=devs)
        field.value = 'sgeulette'
        renderer = ChoiceFieldRenderer(field, self.folder, self.portal.REQUEST)
        self.assertEqual(renderer.render_collection_entry(renderer.context, field.value), u'Stéphan Geulette')

    def test_ChoiceFieldRenderer_render_value_unicode(self):
        # render_collection_entry with non unicode vocabulary value
        devs = SimpleVocabulary([SimpleTerm(value=u'sgeulette', title='Stéphan Geulette')])
        field = schema.Choice(title=u'Test', vocabulary=devs)
        field.value = 'sgeulette'
        renderer = ChoiceFieldRenderer(field, self.folder, self.portal.REQUEST)
        self.assertEqual(renderer.render_value(renderer.context), u'Stéphan Geulette')

    def test_get_exportable_for_fieldname(self):
        member = api.content.create(self.portal, type='member', id='johndoe', languages=['en', 'de'])
        exportable = get_exportable_for_fieldname(member, 'languages', self.portal.REQUEST)
        self.assertTrue(IExportable.providedBy(exportable))
        self.assertEqual(exportable.render_value(member), u'English\nDeutsch')
