from zope.interface import implements
from collective.excelexport.interfaces import IFieldsFactory


class BaseFieldsFactory(object):
    implements(IFieldsFactory)

    portal_types = None
    behaviors = None
    weight = 1000

    def __init__(self, fti):
        self.fti = fti

    def get_fields(self):
        raise NotImplemented
