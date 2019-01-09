# -*- encoding: utf-8 -*-
from Products.ATExtensions.field import FormattableNamesField
from Products.ATExtensions.field import RecordField
from Products.ATExtensions.field import RecordsField
from Products.CMFPlone.utils import safe_unicode
from collective.excelexport.exportables.archetypesfields import BaseFieldRenderer
from zope.component import adapts
from zope.interface import Interface


class FormattableNamesFieldRenderer(BaseFieldRenderer):
    adapts(FormattableNamesField, Interface, Interface)

    def render_value(self, obj):
        subfields = self.field.getSubfields()
        rendered = []
        value = self.get_value(obj)
        for v in value:
            rendered.append(u' '.join([safe_unicode(v[sv]) for sv in subfields if v[sv] and v[sv].strip()]))
        return u', '.join(rendered)


class RecordFieldRenderer(BaseFieldRenderer):
    adapts(RecordField, Interface, Interface)

    def render_record(self, value, subfields):
        return u" ".join([safe_unicode(value[s]) for s in subfields if s in value])

    def render_value(self, obj):
        value = self.get_value(obj)
        if not value:
            return u""
        subfields = self.field.getSubfields()
        return self.render_record(value, subfields)


class RecordsFieldRenderer(RecordFieldRenderer):
    adapts(RecordsField, Interface, Interface)

    def render_value(self, obj):
        value = self.get_value(obj)
        if not value:
            return u""
        subfields = self.field.getSubfields()
        render = []
        for v in value:
            render.append(self.render_record(v, subfields))

        return u", ".join(render)
