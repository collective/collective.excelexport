from zope.interface import implements
from zope.component import adapts

from plone.dexterity.interfaces import IDexterityContent

from collective.excelexport.interfaces import IValueGetter


class ValueGetter(object):
    adapts(IDexterityContent)
    implements(IValueGetter)

    def __init__(self, context):
        self.context = context

    def get(self, fieldname):
        return getattr(self.context, fieldname, None)