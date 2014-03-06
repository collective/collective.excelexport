from zope.interface import implements, Interface
from zope.component import adapts
from zope.schema import getFieldsInOrder

from plone import api
from Products.CMFCore.interfaces import IFolderish

from collective.excelexport.interfaces import IDataSource


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
            title = p_type_fti.Title()
            schema = p_type_fti.lookupSchema()
            fields = [f for f in getFieldsInOrder(schema)]
            data.append({'title': title,
                         'objects': p_types_objects[p_type],
                         'fields': fields})

        return data
