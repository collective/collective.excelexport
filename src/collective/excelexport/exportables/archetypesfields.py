# -*- encoding: utf-8 -*-
from Acquisition import aq_get
from Products.ATContentTypes.interfaces import IATContentType
from Products.Archetypes.interfaces import IField, IFileField, IBooleanField, IDateTimeField, ITextField, ILinesField, \
    IReferenceField
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interfaces import IDynamicViewTypeInformation
from Products.CMFPlone.utils import safe_unicode
from collective.excelexport.exportables.base import BaseExportableFactory
from collective.excelexport.exportables.base import IFieldValueGetter
from collective.excelexport.interfaces import IExportable
from z3c.form.interfaces import NO_VALUE
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.interface import Interface
from zope.interface.declarations import implementer


@implementer(IExportable)
class BaseFieldRenderer(object):

    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def __repr__(self):
        return "<%s - %s>" % (self.__class__.__name__,
                              self.field.__name__)

    def get_value(self, obj):
        return IFieldValueGetter(obj).get(self.field)

    def _translate(self, value):
        if isinstance(value, Message):
            return translate(value, context=self.request)

        return value

    def render_header(self):
        return self._translate(self.field.widget.label)

    def render_value(self, obj):
        value = self.get_value(obj)
        return value

    def render_collection_entry(self, obj, value):
        """Render a value element if the field is a sub field of a collection
        """
        return safe_unicode(value or "")

    def render_style(self, obj, base_style):
        """Gets the style rendering of the
        base_style is the default style of a cell for content
        You can modify base_style, it's already a copy, and return it.
        You can return a Style object with headers and content attributes too.
        """
        return base_style


def get_exportable(field, context, request):
    """Get exportable from dexterity field, context and request
    """
    try:
        # check if there is a specific adapter for the field name
        exportable = getMultiAdapter(
            (field, context, request),
            interface=IExportable,
            name=field.__name__)
    except ComponentLookupError:
        # get the generic adapter for the field
        exportable = getMultiAdapter(
            (field, context, request),
            interface=IExportable)

    return exportable


class ArchetypesFieldsExportableFactory(BaseExportableFactory):
    """Get fields content schema
    """
    adapts(IDynamicViewTypeInformation, Interface, Interface)
    weight = 100

    def get_exportables(self):
        archetype_tool = getToolByName(self.context, 'archetype_tool')
        schema = archetype_tool.lookupType(self.fti.product, self.fti.content_meta_type)['schema']
        fields = schema.fields()
        exportables = []
        for field in fields:
            exportables.append(get_exportable(field, self.context, self.request))

        return exportables


@implementer(IFieldValueGetter)
class ArchetypesValueGetter(object):
    adapts(IATContentType)

    def __init__(self, context):
        self.context = context

    def get(self, field):
        accessor = field.getAccessor(self.context)
        if accessor:
            return accessor()
        else:
            return aq_get(self.context, field.id, None)


class FieldRenderer(BaseFieldRenderer):
    adapts(IField, Interface, Interface)


class FileFieldRenderer(BaseFieldRenderer):
    adapts(IFileField, Interface, Interface)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        return value and value.filename or u""


class BooleanFieldRenderer(BaseFieldRenderer):
    adapts(IBooleanField, Interface, Interface)

    def render_value(self, obj):
        value = self.get_value(obj)
        return value and 1 or 0


class DateFieldRenderer(BaseFieldRenderer):
    adapts(IDateTimeField, Interface, Interface)

    def render_collection_entry(self, obj, value):
        return value.strftime("%Y/%m/%d")

    def render_style(self, obj, base_style):
        base_style.num_format_str = 'yyyy/mm/dd'
        return base_style


class LinesFieldRenderer(BaseFieldRenderer):
    adapts(ILinesField, Interface, Interface)

    def _get_vocabulary_value(self, obj, value):
        if not value:
            return value

        return self.field.Vocabulary(obj).getValue(value)

    def render_value(self, obj):
        value = self.get_value(obj)
        if self.field.vocabulary:
            vocabulary = self.field.Vocabulary(obj)
            value = ', '.join([vocabulary.getValue(v) or v for v in value])
        else:
            value = ', '.join(value)

        return value


class TextFieldRenderer(BaseFieldRenderer):
    adapts(ITextField, Interface, Interface)

    truncate_at = 47

    def _get_text(self, value):
        return value

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        if not value or value == NO_VALUE:
            return ""

        text = safe_unicode(self._get_text(value))
        if len(text) > self.truncate_at + 3:
            return text[:self.truncate_at] + u"..."

        return text


class ReferenceFieldRenderer(BaseFieldRenderer):
    adapts(IReferenceField, Interface, Interface)

    def render_value(self, obj):
        value = self.get_value(obj)
        if self.field.multiValued:
            return u', '.join([self.render_collection_entry(obj, v) for v in value])
        else:
            return self.render_collection_entry(obj, value)

    def render_collection_entry(self, obj, value):
        try:
            return safe_unicode(value.Title()) if value else u""
        except AttributeError:
            return value.id
