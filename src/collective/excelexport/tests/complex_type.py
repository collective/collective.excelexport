# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements
from collective.excelexport.tests.object_factory import ObjectField
from collective.excelexport.tests.object_factory import register_object_factories


class IObjectSchema(model.Schema):
    field1 = schema.TextLine(title=u"Field 1")
    field2 = schema.TextLine(title=u"Field 2")


class IComplex(model.Schema):

    title = schema.TextLine(title=u"Title")
    object_field = ObjectField(title=u"Address", schema=IObjectSchema)


class Complex(Container):
    implements(IComplex)


register_object_factories(IComplex)
