from zope.schema.interfaces import IField, IDate, ICollection
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts

from plone.namedfile.editor import INamedFileField

from collective.excelexport.interfaces import IFieldRenderer
from zope.component._api import getMultiAdapter


class BaseFieldRenderer(object):
    implements(IFieldRenderer)

    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def render_header(self):
        return self.field.title

    def render_value(self, value):
        """Gets the value to render in excel file from content value
        """
        return value

    def render_style(self, value, base_style):
        """Gets the style rendering of the
        base_style is the default style of a cell for content
        """
        return base_style


class FieldRenderer(BaseFieldRenderer):
    adapts(IField, Interface, Interface)


class FileFieldRenderer(BaseFieldRenderer):
    adapts(INamedFileField, Interface, Interface)

    def render_value(self, value):
        """Gets the value to render in excel file from content value
        """
        return value and value.filename or ""


class DateFieldRenderer(BaseFieldRenderer):
    adapts(IDate, Interface, Interface)

    def render_value(self, value):
        """Gets the value to render in excel file from content value
        """
        return value

    def render_style(self, value, base_style):
        base_style.num_format_str = 'yyyy/mm/dd'
        return base_style


class CollectionFieldRenderer(BaseFieldRenderer):
    adapts(ICollection, Interface, Interface)

    def render_value(self, value):
        """Gets the value to render in excel file from content value
        """
        sub_renderer = getMultiAdapter((self.field.value_type,
                                        self.context, self.request),
                                        interface=IFieldRenderer)
        return value and "\n".join([str(sub_renderer.render_value(v))
                                    for v in value]) or ""

try:
    from z3c.relationfield.interfaces import IRelation
    HAS_RELATIONFIELD = True
    class RelationFieldRenderer(BaseFieldRenderer):
        adapts(IRelation, Interface, Interface)

        def render_value(self, value):
            return value and value.to_object.Title() or u""

except:
    HAS_RELATIONFIELD = False

