# -*- encoding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFPlone.utils import safe_unicode
from collective.excelexport.exportables.base import BaseExportableFactory
from collective.excelexport.interfaces import IExportable
from plone import api
from plone.app.textfield import RichText
from plone.app.textfield.interfaces import IRichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.field import NamedFile
from plone.namedfile.field import NamedImage
from plone.namedfile.interfaces import INamedField
from plone.schemaeditor.schema import IChoice
from plone.supermodel.interfaces import FIELDSETS_KEY
from z3c.form.interfaces import NO_VALUE
from zope import schema
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.interface import Interface
from zope.interface.declarations import implementer
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import (
    IField,
    IDate,
    ICollection,
    IVocabularyFactory,
    IBool,
    IText,
    IDatetime,
)

excluded_object_fields = (
    NamedBlobFile,
    NamedBlobImage,
    NamedFile,
    NamedImage,
    RichText,
)


class FieldWrapper(object):
    def __init__(self, field):
        self.field = field

    def __getattr__(self, name):
        return getattr(self.field, name)


class ParentField(FieldWrapper):
    def bind(self, obj):
        return self.field.bind(obj.__parent__)


class GrandParentField(FieldWrapper):
    def bind(self, obj):
        return self.field.bind(obj.__parent__.__parent__)


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
    ordered_fieldsets = ["default"]
    for fieldset in schema.queryTaggedValue(FIELDSETS_KEY, []):
        ordered_fieldsets.append(fieldset.__name__)
        fieldset_fields[fieldset.__name__] = fieldset.fields

    if fieldset_fields.get("default", []):
        fieldset_fields["default"] += non_fieldset_fields(schema)
    else:
        fieldset_fields["default"] = non_fieldset_fields(schema)

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

        fieldset_fields["default"].extend(non_fieldset_fields(schema))

    ordered_fields = []
    for fieldset in ordered_fieldsets:
        ordered_fields.extend(fieldset_fields[fieldset])

    fields.sort(key=lambda field: ordered_fields.index(field[0]))
    fields = extend_object_fields(fields)

    return fields


def extend_object_fields(fields):
    new_fields = []
    for key, field in fields:
        if isinstance(field, schema.Object) and not isinstance(
            field, excluded_object_fields
        ):
            for f_key, subfield in getFieldsInOrder(field.schema):
                new_fields.append(((key, f_key), (field, subfield)))
        else:
            new_fields.append((key, field))
    return new_fields


def get_exportable(field, context, request):
    """Get exportable from dexterity field, context and request
    """
    if isinstance(field, tuple):
        parent_field, field = field
        field_name = "{0}.{1}".format(parent_field.__name__, field.__name__)
    else:
        parent_field = None
        field_name = field.__name__
    try:
        # check if there is a specific adapter for the field name
        exportable = getMultiAdapter(
            (field, context, request), interface=IExportable, name=field_name
        )
    except ComponentLookupError:
        # get the generic adapter for the field
        exportable = getMultiAdapter((field, context, request), interface=IExportable)

    if parent_field is not None:
        exportable.define_parent(parent_field)

    return exportable


def get_exportable_for_fieldname(context, fieldname, request):
    """Get exportable from dexterity fieldname, context and request
    """
    # get the field
    field = filter(
        lambda x: x[0] == fieldname, get_ordered_fields(context.getTypeInfo())
    )[0][1]
    return get_exportable(field, context, request)


class DexterityFieldsExportableFactory(BaseExportableFactory):
    """Get fields content schema
    """

    adapts(IDexterityFTI, Interface, Interface)
    weight = 100

    def get_exportables(self):
        fields = get_ordered_fields(self.fti)
        exportables = []
        for field in fields:
            exportables.append(get_exportable(field[1], self.context, self.request))

        return exportables


class IFieldValueGetter(Interface):
    """Adapter to get a value from fieldname
    """

    def get(self, fieldname):
        """Get value from fieldname
        """


@implementer(IFieldValueGetter)
class DexterityValueGetter(object):
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def get(self, field):
        value = getattr(aq_base(self.context), field.__name__, None)
        if hasattr(value, "__call__"):
            value = value()
        return value


@implementer(IExportable)
class BaseFieldRenderer(object):
    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request
        self.parent_field = None

    def __repr__(self):
        return "<%s - %s>" % (self.__class__.__name__, self.field.__name__)

    def get_value(self, obj):
        if self.parent_field is not None:
            return getattr(
                IFieldValueGetter(obj).get(self.parent_field), self.field.__name__, None
            )
        return IFieldValueGetter(obj).get(self.field)

    def define_parent(self, parent_field):
        self.parent_field = parent_field

    def _translate(self, value):
        if isinstance(value, Message):
            return translate(value, context=self.request)

        return value

    def render_header(self):
        if self.parent_field is not None:
            return safe_unicode("{0} - {1}").format(
                self._translate(self.parent_field.title),
                self._translate(self.field.title),
            )
        return self._translate(self.field.title)

    def render_value(self, obj):
        value = self.get_value(obj)
        if value == NO_VALUE:
            return None
        else:
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


class FieldRenderer(BaseFieldRenderer):
    adapts(IField, Interface, Interface)


class FileFieldRenderer(BaseFieldRenderer):
    adapts(INamedField, Interface, Interface)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        return value and value.filename or u""


class BooleanFieldRenderer(BaseFieldRenderer):
    adapts(IBool, Interface, Interface)

    def render_value(self, obj):
        value = self.get_value(obj)
        return value and 1 or 0


class DateFieldRenderer(BaseFieldRenderer):
    adapts(IDate, Interface, Interface)

    def render_value(self, obj):
        value = self.get_value(obj)
        if value == NO_VALUE or not value:
            return None
        else:
            return value.strftime("%Y/%m/%d")

    def render_collection_entry(self, obj, value):
        if not value:
            return u""
        return value.strftime("%Y/%m/%d")

    def render_style(self, obj, base_style):
        base_style.num_format_str = "yyyy/mm/dd"
        return base_style


class DateTimeFieldRenderer(BaseFieldRenderer):
    adapts(IDatetime, Interface, Interface)

    def render_value(self, obj):
        value = self.get_value(obj)
        if value == NO_VALUE or not value:
            return None
        else:
            return value.strftime("%Y/%m/%d %H:%M")

    def render_collection_entry(self, obj, value):
        if not value:
            return u""
        return value.strftime("%Y/%m/%d %H:%M")

    def render_style(self, obj, base_style):
        base_style.num_format_str = "yyyy/mm/dd"
        return base_style


class ChoiceFieldRenderer(BaseFieldRenderer):
    adapts(IChoice, Interface, Interface)

    def _get_vocabulary_value(self, obj, value):
        res = value
        if res:
            vocabulary = self.field.vocabulary
            # for source vocabulary
            if IContextSourceBinder.providedBy(vocabulary):
                vocabulary = vocabulary(obj)
            # for named vocabulary
            if not vocabulary:
                vocabularyName = self.field.vocabularyName
                if vocabularyName:
                    vocabulary = getUtility(IVocabularyFactory, name=vocabularyName)(
                        obj
                    )

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
                    res = value
                else:
                    res = title
            else:
                res = value
        return safe_unicode(res)

    def render_value(self, obj):
        value = self.get_value(obj)
        voc_value = self._get_vocabulary_value(obj, value)
        return voc_value

    def render_collection_entry(self, obj, value):
        voc_value = self._get_vocabulary_value(obj, value)
        return voc_value and translate(voc_value, context=self.request) or u""


class CollectionFieldRenderer(BaseFieldRenderer):
    adapts(ICollection, Interface, Interface)

    separator = u"\n"

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        value_type = self.field.value_type
        if not value_type:
            value_type = self.field

        sub_renderer = getMultiAdapter(
            (value_type, self.context, self.request), interface=IExportable
        )

        return (
            value
            and self.separator.join(
                [sub_renderer.render_collection_entry(obj, v) for v in value]
            )
            or u""
        )


class TextFieldRenderer(BaseFieldRenderer):
    adapts(IText, Interface, Interface)

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
            return text[: self.truncate_at] + u"..."

        return text


class RichTextFieldRenderer(TextFieldRenderer):
    adapts(IRichText, Interface, Interface)

    def _get_text(self, value):
        ptransforms = api.portal.get_tool("portal_transforms")
        return ptransforms.convert("html_to_text", value.output).getData().strip()


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
                sub_renderer = getMultiAdapter(
                    (field, self.context, self.request), interface=IExportable
                )
                field_renderings.append(
                    u"%s : %s"
                    % (
                        sub_renderer.render_header(),
                        sub_renderer.render_collection_entry(obj, value.get(fieldname)),
                    )
                )

            return u" / ".join([r for r in field_renderings])

        def render_value(self, obj):
            value = self.get_value(obj)
            return self.render_collection_entry(obj, value)


except:
    HAS_DATAGRIDFIELD = False
