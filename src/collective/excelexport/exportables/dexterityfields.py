from zope.interface import Interface
from zope.schema.interfaces import IField, IDate, ICollection,\
    IVocabularyFactory
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


class DexterityFieldsExportableFactory(BaseExportableFactory):
    """Get fields content schema
    """
    adapts(IDexterityFTI, Interface, Interface)

    def get_exportables(self):
        schema = self.fti.lookupSchema()
        fields = [f[1] for f in getFieldsInOrder(schema)]
        exportables = [getMultiAdapter((field, self.context, self.request),
                                        interface=IExportable) for field in fields]
        return exportables


class DexterityBehaviorsExportableFactory(BaseExportableFactory):
    """Get fields from behaviors
    """
    adapts(IDexterityFTI, Interface, Interface)

    def get_exportables(self):
        fields = []
        for behavior_id in self.fti.behaviors:
            behavior = getUtility(IBehavior, behavior_id).interface
            if not IFormFieldProvider.providedBy(behavior):
                continue

            fields.extend([f[1] for f in getFieldsInOrder(behavior)])

        exportables = [getMultiAdapter((field, self.context, self.request),
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

    def get_value(self, obj):
        return IFieldValueGetter(obj).get(self.field)

    def render_header(self):
        return translate(self.field.title, context=self.request)

    def render_value(self, obj):
        return self.get_value(obj)

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
            return term.title or value
        else:
            return value

    def render_value(self, obj):
        value = self.get_value(obj)
        voc_value = self._get_vocabulary_value(obj, value)
        return voc_value

    def render_collection_entry(self, obj, value):
        voc_value = self._get_vocabulary_value(obj, value)
        return voc_value and translate(voc_value, context=self.request) or ""


class CollectionFieldRenderer(BaseFieldRenderer):
    adapts(ICollection, Interface, Interface)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        sub_renderer = getMultiAdapter((self.field.value_type,
                                        self.context, self.request),
                                        interface=IExportable)
        return value and "\n".join([str(sub_renderer.render_collection_entry(obj, v))
                                    for v in value]) or ""


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
            return text[:47] + "..."


try:
    from z3c.relationfield.interfaces import IRelation
    HAS_RELATIONFIELD = True
    class RelationFieldRenderer(BaseFieldRenderer):
        adapts(IRelation, Interface, Interface)

        def render_value(self, obj):
            value = self.get_value(obj)
            return self.render_collection_entry(obj, value)

        def render_collection_entry(self, obj, value):
            return value and value.to_object.Title() or u""

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
                field_renderings.append("%s : %s" % (
                                        sub_renderer.render_header(),
                                        sub_renderer.render_collection_entry(obj,
                                                value.get(fieldname))))

            return " / ".join([r for r in field_renderings])

        def render_value(self, obj):
            value = self.get_value(obj)
            return self.render_collection_entry(obj, value)

except:
    HAS_DATAGRIDFIELD = False


try:
    from collective.contact.widget.interfaces import IContactChoice
    HAS_CONTACTS = True
    class ContactFieldRenderer(BaseFieldRenderer):
        adapts(IContactChoice, Interface, Interface)

        def render_value(self, obj):
            value = self.get_value(obj)
            return self.render_collection_entry(obj, value)

        def render_collection_entry(self, obj, value):
            return value and value.to_object and value.to_object.get_full_title() or u""

except:
    HAS_CONTACTS = False