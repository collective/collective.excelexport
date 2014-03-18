from zope.component import adapts
from zope.interface import Interface

from collective.excelexport.exportables.dexterityfields import BaseFieldRenderer
from collective.contact.widget.interfaces import IContactChoice


class ContactFieldRenderer(BaseFieldRenderer):
    adapts(IContactChoice, Interface, Interface)

    def render_value(self, obj):
        value = self.get_value(obj)
        return self.render_collection_entry(obj, value)

    def render_collection_entry(self, obj, value):
        return value and value.to_object and value.to_object.get_full_title() or u""
