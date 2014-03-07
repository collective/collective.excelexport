from zope.interface import implements, Interface
from zope.component import adapts
from zope.component import getAdapters
from zope.component import getUtility
from datetime import datetime

from plone import api
from plone.behavior.interfaces import IBehavior
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

    def get_filename(self):
        return "%s-%s" % (
                datetime.now().strftime("%d-%m-%Y"), self.context.getId())

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
            # get exportables for each content type
            p_type_fti = ttool[p_type]
            factories = getAdapters((p_type_fti, self.context, self.request),
                                    IExportableFactory)
            filtered_factories = []
            for factory in factories:
                factory = factory[1]
                if factory.portal_types and p_type not in factory.portal_types:
                    # filter on content types if it is set
                    continue

                if factory.behaviors:
                    # filter on behaviors if it is set
                    for behavior_id in p_type_fti.behaviors:
                        behavior = getUtility(IBehavior, behavior_id).interface
                        if behavior in factory.behaviours:
                            break
                    else:
                        continue

                filtered_factories.append(factory)

            # get the list of exportables from factories
            exportables = []
            for factory in filtered_factories:
                exportables.extend(factory.get_exportables())

            title  = p_type_fti.Title()
            data.append({'title': title,
                         'objects': p_types_objects[p_type],
                         'exportables': exportables})

        return data

