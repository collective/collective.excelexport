from zope.schema.interfaces import IField, IDate, ICollection
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter

from plone.namedfile.editor import INamedFileField
from plone.dexterity.interfaces import IDexterityContent

from collective.excelexport.interfaces import IExportable


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
        return self.field.title

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        return self.get_value(obj)

    def render_collection_entry(self, value):
        return str(value or "")

    def render_style(self, value, base_style):
        """Gets the style rendering of the
        base_style is the default style of a cell for content
        """
        return base_style


class FieldRenderer(BaseFieldRenderer):
    adapts(IField, Interface, Interface)


class FileFieldRenderer(BaseFieldRenderer):
    adapts(INamedFileField, Interface, Interface)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        return value and value.filename or ""


class DateFieldRenderer(BaseFieldRenderer):
    adapts(IDate, Interface, Interface)

    def render_collection_entry(self, value):
        return value.strftime("%Y/%m/%d")

    def render_style(self, obj, base_style):
        base_style.num_format_str = 'yyyy/mm/dd'
        return base_style


class CollectionFieldRenderer(BaseFieldRenderer):
    adapts(ICollection, Interface, Interface)

    def render_value(self, obj):
        """Gets the value to render in excel file from content value
        """
        value = self.get_value(obj)
        sub_renderer = getMultiAdapter((self.field.value_type,
                                        self.context, self.request),
                                        interface=IExportable)
        return value and "\n".join([str(sub_renderer.render_collection_entry(v))
                                    for v in value]) or ""

try:
    from z3c.relationfield.interfaces import IRelation
    HAS_RELATIONFIELD = True
    class RelationFieldRenderer(BaseFieldRenderer):
        adapts(IRelation, Interface, Interface)

        def render_collection_entry(self, value):
            return value and value.to_object.Title() or u""

        def render_value(self, obj):
            value = self.get_value(obj)
            return value and value.to_object.Title() or u""

except:
    HAS_RELATIONFIELD = False

