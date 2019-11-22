from collective.excelexport.interfaces import IExportableFactory

from zope.interface import implementer, Interface


class IFieldValueGetter(Interface):
    """Adapter to get a value from fieldname
    """

    def get(self, fieldname):
        """Get value from fieldname
        """


@implementer(IExportableFactory)
class BaseExportableFactory(object):
    portal_types = None
    behaviors = None
    weight = 1000

    def __init__(self, fti, context, request):
        self.fti = fti
        self.context = context
        self.request = request

    def get_exportables(self):
        raise NotImplemented
