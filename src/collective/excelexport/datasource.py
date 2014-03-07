from zope.interface import implements, Interface
from zope.component import adapts
from zope.component import getAdapters

from plone import api
from Products.CMFCore.interfaces import IFolderish

from collective.excelexport.interfaces import IDataSource
from collective.excelexport.interfaces import IExportableFactory


class DataSource(object):
    """Gets the fields and objects to serialize in excel file
    provided by a named adapter that adapts the context and the request
    """
    implements(IDataSource)
    adapts(IFolderish, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_objects(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(REQUEST=self.request,
                                       path={'query': '/'.join(self.context.getPhysicalPath()),
                                             'depth': 1})
        return [b.getObject() for b in brains]


    def get_sheets_data(self):
        """Gets a list of dictionaries with three keys :
            title: the title of the sheet
            objects: the list of objects
            fields: the names of the fields to render
        """
        objects = self.get_objects()
        p_types_objects = {}
        for obj in objects:
            p_types_objects.setdefault(obj.portal_type, []).append(obj)

        ttool = api.portal.get_tool('portal_types')
        data = []
        for p_type in sorted(p_types_objects.keys()):
            p_type_fti = ttool[p_type]
            factories = getAdapters((p_type_fti, self.context, self.request),
                                    IExportableFactory)
            factories = [factory[1] for factory in factories
                         if not factory[1].portal_types
                         or p_type in factory[1].portal_types]

            exportables = []
            for factory in factories:
                exportables.extend(factory.get_exportables())

            title  = p_type_fti.Title()
            data.append({'title': title,
                         'objects': p_types_objects[p_type],
                         'exportables': exportables})

        return data

