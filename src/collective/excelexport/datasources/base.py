from zope.interface import implements
from zope.component import getAdapters
from zope.component import getUtility

from plone import api
from plone.behavior.interfaces import IBehavior

from collective.excelexport.interfaces import IDataSource
from collective.excelexport.interfaces import IExportableFactory


class BaseContentsDataSource(object):
    """
    Base class for a datasource that exports contents
    Gets the fields and objects to serialize in excel file
    provided by a named adapter that adapts the fti, the context and the request

    group them by portal type (one sheet by portal type)
    """
    implements(IDataSource)
    portal_types = None
    behaviors = None
    excluded_factories = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_filename(self):
        raise NotImplemented

    def get_objects(self):
        raise NotImplemented

    def filter_exportables(self, exportables):
        """You can filter exportables here
        """
        return exportables

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
            for factory in sorted(factories, key=lambda f:f[1].weight):
                factory_name, factory = factory
                if factory.portal_types and p_type not in factory.portal_types:
                    # filter on content types if it is set
                    continue
                if self.excluded_factories and factory_name in self.excluded_factories:
                    continue

                if factory.behaviors:
                    # filter on behaviors if it is set
                    for behavior_id in p_type_fti.behaviors:
                        behavior = getUtility(IBehavior, behavior_id).interface
                        if behavior in factory.behaviors:
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
                         'exportables': self.filter_exportables(exportables)})

        return data
