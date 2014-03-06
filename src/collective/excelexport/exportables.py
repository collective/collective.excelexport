from zope.interface.interface import Interface
from zope.component import adapts
from zope.schema import getFieldsInOrder
from zope.component import getMultiAdapter
from zope.interface.declarations import implements

from plone.dexterity.interfaces import IDexterityFTI

from collective.excelexport.interfaces import IExportable
from collective.excelexport.interfaces import IExportableFactory


class DexterityFieldsExportableFactory(object):
    adapts(IDexterityFTI, Interface, Interface)
    implements(IExportableFactory)

    portal_types = None

    def __init__(self, fti, context, request):
        self.fti = fti
        self.context = context
        self.request = request

    def get_exportables(self):
        schema = self.fti.lookupSchema()
        fields = [f[1] for f in getFieldsInOrder(schema)]
        exportables = [getMultiAdapter((field, self.context, self.request),
                                        interface=IExportable) for field in fields]
        return exportables
