from zope.interface import implements
from collective.excelexport.interfaces import IExportableFactory


class BaseExportableFactory(object):
    implements(IExportableFactory)

    portal_types = None
    behaviors = None
    weight = 1000

    def __init__(self, fti, context, request):
        self.fti = fti
        self.context = context
        self.request = request

    def get_exportables(self):
        raise NotImplemented
