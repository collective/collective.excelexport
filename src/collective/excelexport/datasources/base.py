from zope.interface import implements
from zope.component import getAdapters
from zope.component import getUtility
from zope.component import queryUtility

from plone import api
from plone.behavior.interfaces import IBehavior

from collective.excelexport.interfaces import IDataSource
from collective.excelexport.interfaces import IFieldsFactory


class BaseContentsDataSource(object):
    """
    Base class for a datasource that exports contents
    Gets the fields and objects to serialize in excel file
    provided by a named adapter that adapts the fti, the context and the request

    group them by portal type (one sheet by portal type)
    """
    implements(IDataSource)
    excluded_factories = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_filename(self):
        raise NotImplemented

    def get_objects(self):
        raise NotImplemented

    def filter(self, fields):
        """You can filter fields here
        """
        return fields

    def get_factories(self, p_type_fti):
        factories = getAdapters((p_type_fti, ),
                                IFieldsFactory)
        filtered_factories = []
        for factory_name, factory in sorted(factories, key=lambda f: f[1].weight):
            if factory.portal_types and p_type_fti.id not in factory.portal_types:
                # filter on content types if it is set
                continue
            elif self.excluded_factories and factory_name in self.excluded_factories:
                # exclude factory if there is a factory filter
                continue
            elif factory.behaviors:
                # filter on behaviors if factory is restricted to a behavior
                for behavior_id in p_type_fti.behaviors:
                    behavior = getUtility(IBehavior, behavior_id).interface
                    if behavior in factory.behaviors:
                        break
                else:
                    continue

            filtered_factories.append(factory)

        # get fields factory per portal_type
        factory = queryUtility(IFieldsFactory, name=p_type_fti.getId())
        if factory:
            filtered_factories.append(factory)

        return filtered_factories

    def get_sheets_data(self):
        """Gets a list of dictionaries with three keys :
            title: the title of the sheet
            objects: the list of objects
            fields: the fields to render
        """
        objects = self.get_objects()
        p_types_objects = {}
        for obj in objects:
            p_types_objects.setdefault(obj.portal_type, []).append(obj)

        ttool = api.portal.get_tool('portal_types')
        data = []
        for p_type in sorted(p_types_objects.keys()):
            # get fields for each content type
            p_type_fti = ttool[p_type]
            factories = self.get_factories(p_type_fti)

            # get the list of fields from factories
            fields = []
            for factory in factories:
                fields.extend(factory.get_fields())

            title = p_type_fti.Title()
            data.append({'title': title,
                         'objects': p_types_objects[p_type],
                         'fields': self.filter(fields)
                        })

        return data
