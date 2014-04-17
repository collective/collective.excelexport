# -*- encoding: utf-8 -*-
from zope.interface import Interface
from zope.schema.interfaces import IField, IDate, ICollection,\
    IVocabularyFactory, IBool
from zope.schema import getFieldsInOrder
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component._api import getUtility
from zope.i18n import translate
from zope.interface.declarations import implements

from z3c.form.interfaces import NO_VALUE

from Products.CMFCore.utils import getToolByName
from plone.app.textfield.interfaces import IRichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedField
from plone.schemaeditor.schema import IChoice

from collective.excelexport.interfaces import IExportable
from collective.excelexport.exportables.base import BaseExportableFactory
from plone.supermodel.interfaces import FIELDSETS_KEY


def non_fieldset_fields(schema):
    fieldset_fields = []
    fieldsets = schema.queryTaggedValue(FIELDSETS_KEY, [])

    for fieldset in fieldsets:
        fieldset_fields.extend(fieldset.fields)

    fields = [info[0] for info in getFieldsInOrder(schema)]
    return [f for f in fields if f not in fieldset_fields]


def get_ordered_fields(fti):
    # this code is much complicated because we have to get sure
    # we get the fields in the order of the fieldsets
    # the order of the fields in the fieldsets can differ
    # of the getFieldsInOrder(schema) order...
    # that's because fields from different schemas
    # can take place in the same fieldset
    schema = fti.lookupSchema()
    fieldset_fields = {}
    ordered_fieldsets = ['default']
    for fieldset in schema.queryTaggedValue(FIELDSETS_KEY, []):
        ordered_fieldsets.append(fieldset.__name__)
        fieldset_fields[fieldset.__name__] = fieldset.fields

    fieldset_fields['default'] = non_fieldset_fields(schema)

    # Get the behavior fields
    fields = getFieldsInOrder(schema)
    for behavior_id in fti.behaviors:
        schema = getUtility(IBehavior, behavior_id).interface
        if not IFormFieldProvider.providedBy(schema):
            continue

        fields.extend(getFieldsInOrder(schema))
        for fieldset in schema.queryTaggedValue(FIELDSETS_KEY, []):
            fieldset_fields.setdefault(fieldset.__name__, []).extend(fieldset.fields)
            ordered_fieldsets.append(fieldset.__name__)

        fieldset_fields['default'].extend(non_fieldset_fields(schema))

    ordered_fields = []
    for fieldset in ordered_fieldsets:
        ordered_fields.extend(fieldset_fields[fieldset])

    fields.sort(key=lambda field: ordered_fields.index(field[0]))
    return fields


class DexterityFieldsExportableFactory(BaseExportableFactory):
    """Get fields content schema
    """
    adapts(IDexterityFTI, Interface, Interface)
    weight = 100

    def get_exportables(self):
        fields = get_ordered_fields(self.fti)
        exportables = [getMultiAdapter((field[1], self.context, self.request),
                                        interface=IExportable) for field in fields]
        return exportables


class IFieldValueGetter(Interface):
    """Adapter to get a value from fieldname
    """

    def get(self, fieldname):
        """Get value from fieldname
        """

class DexterityValueGetter(object):
    adapts(IDexterityContent)
    implements(IFieldValueGetter)

    def __init__(self, context):
        self.context = context

    def get(self, field):
        return getattr(self.context, field.__name__, None)


class BaseFieldRenderer(object):
    implements(IExportable)

    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def __repr__(self):
        return "<%s - %s>" % (self.__class__.__name__,
                                   self.field.__name__)

    def get_value(self, obj):
        return IFieldValueGetter(obj).get(self.field)

    def render_header(self):
        return self.field.title

    def render_value(self, obj):
        value = self.get_value(obj)
        if value == NO_VALUE:
            return None
        else:
            return value

    def render_collection_entry(self, obj, value):
        """Render a value element if the field is a sub field of a collection
        """
        return str(value or "")

    def render_style(self, value, base_style):
        """Gets the style rendering of the
        base_style is the default style of a cell for content
        """
        return base_style


class FieldRenderer(BaseFieldRenderer):
    adapts(IField, Interface, Interface)


class FileFieldRenderer(BaseFieldRenderer):
    adapts(INamedField, Interface, Interface)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        return value and value.filename or ""


class BooleanFieldRenderer(BaseFieldRenderer):
    adapts(IBool, Interface, Interface)

    def render_value(self, obj):
        value = self.get_value(obj)
        return value and 1 or 0


class DateFieldRenderer(BaseFieldRenderer):
    adapts(IDate, Interface, Interface)

    def render_collection_entry(self, obj, value):
        return value.strftime("%Y/%m/%d")

    def render_style(self, obj, base_style):
        base_style.num_format_str = 'yyyy/mm/dd'
        return base_style


class ChoiceFieldRenderer(BaseFieldRenderer):
    adapts(IChoice, Interface, Interface)

    def _get_vocabulary_value(self, obj, value):
        if not value:
            return value

        vocabulary = self.field.vocabulary
        if not vocabulary:
            vocabularyName = self.field.vocabularyName
            if vocabularyName:
                vocabulary = getUtility(IVocabularyFactory, name=vocabularyName)(obj)

        if vocabulary:
            try:
                term = vocabulary.getTermByToken(value)
            except LookupError:
                term = None
        else:
            term = None

        if term:
            title = term.title
            if not title:
                return value
            else:
                return title
        else:
            return value

    def render_value(self, obj):
        value = self.get_value(obj)
        voc_value = self._get_vocabulary_value(obj, value)
        return voc_value

    def render_collection_entry(self, obj, value):
        voc_value = self._get_vocabulary_value(obj, value)
        return voc_value and translate(voc_value, context=self.request) or u""


class CollectionFieldRenderer(BaseFieldRenderer):
    adapts(ICollection, Interface, Interface)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        sub_renderer = getMultiAdapter((self.field.value_type,
                                        self.context, self.request),
                                        interface=IExportable)
        return value and u"\n".join([sub_renderer.render_collection_entry(obj, v)
                                     for v in value]) or u""


class RichTextFieldRenderer(BaseFieldRenderer):
    adapts(IRichText, Interface, Interface)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        if not value or value == NO_VALUE:
            return ""

        ptransforms = getToolByName(obj, 'portal_transforms')
        text = ptransforms.convert('text_to_html', value.output).getData()
        if len(text) > 50:
            return text[:47] + u"..."


try:
    from z3c.relationfield.interfaces import IRelation
    HAS_RELATIONFIELD = True
    class RelationFieldRenderer(BaseFieldRenderer):
        adapts(IRelation, Interface, Interface)

        def render_value(self, obj):
            value = self.get_value(obj)
            return self.render_collection_entry(obj, value)

        def render_collection_entry(self, obj, value):
            return value and value.to_object and value.to_object.Title() or u""

except:
    HAS_RELATIONFIELD = False


try:
    from collective.z3cform.datagridfield.interfaces import IRow
    HAS_DATAGRIDFIELD = True
    class DictRowFieldRenderer(BaseFieldRenderer):
        adapts(IRow, Interface, Interface)

        def render_collection_entry(self, obj, value):
            fields = getFieldsInOrder(self.field.schema)
            field_renderings = []
            for fieldname, field in fields:
                sub_renderer = getMultiAdapter((field,
                                                self.context, self.request),
                                                interface=IExportable)
                field_renderings.append(u"%s : %s" % (
                                        sub_renderer.render_header(),
                                        sub_renderer.render_collection_entry(obj,
                                                value.get(fieldname))))

            return u" / ".join([r for r in field_renderings])

        def render_value(self, obj):
            value = self.get_value(obj)
            return self.render_collection_entry(obj, value)

except:
    HAS_DATAGRIDFIELD = False
