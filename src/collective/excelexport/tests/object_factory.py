# -*- coding: utf-8 -*-

from z3c.form.field import Fields
from z3c.form.interfaces import IObjectFactory
from z3c.form.object import FactoryAdapter
from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import implementer
from zope.schema import Object
from zope.schema.fieldproperty import FieldProperty

import sys


class ObjectField(Object):
    pass


class GenericObject(object):
    """Baseclass for generic object registration"""

    __name__ = ""
    __parent__ = None

    def getId(self):
        return self.__name__ or ""

    def __repr__(self):
        return "<GenericObject>"


class GenericObjectAdapter(FactoryAdapter):
    pass


def generic_object_adapter(factory):
    return type("GenericObjectAdapter", (GenericObjectAdapter,), {"factory": factory})


def register_object_factories(schema):
    """Register generic adapters for schema `Object` type"""
    manager = getGlobalSiteManager()
    for name, field in get_fields_from_schema(schema):
        if isinstance(field.field, ObjectField):
            f_schema = field.field.schema
            obj_name = "GenericObject{0}{1}".format(name[0].upper(), name[1:])
            f_object = type(
                obj_name,
                (GenericObject,),
                {n: FieldProperty(f_schema[n]) for n, f in Fields(f_schema).items()},
            )
            setattr(sys.modules[__name__], obj_name, f_object)
            factory = implementer(f_schema)(f_object)
            manager.registerAdapter(
                generic_object_adapter(factory),
                required=(Interface, Interface, Interface, Interface),
                provided=IObjectFactory,
                name=f_schema.__identifier__,
            )


def get_fields_from_schema(schema):
    fields = []
    for name, field in Fields(schema).items():
        fields.append((name, field))
        if hasattr(field.field, "value_type"):
            # Ensure that sequence field are correctly processed
            field.field = field.field.value_type
        if hasattr(field.field, "schema"):
            fields.extend(get_fields_from_schema(field.field.schema))
    return fields
