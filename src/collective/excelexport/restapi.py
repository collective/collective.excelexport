import datetime
from copy import deepcopy

from collective.excelexport.datasources.base import BaseContentsDataSource
from plone import api
from plone.rest.service import Service
from plone.restapi.interfaces import IZCatalogCompatibleQuery
from plone.restapi.search.utils import unflatten_dotted_dict
from zope.component import adapts, getMultiAdapter
from zope.interface import Interface

RESTAPI_POLICY = 'excelexport.restapi.search'


class CollectiveExcelexport(Service):

    def render(self):
        if 'excelexport.policy' not in self.request.form:
            self.request.form['excelexport.policy'] = RESTAPI_POLICY
        return self.context.restrictedTraverse('@@collective.excelexport')()


class CollectiveExcelexportCsv(Service):

    def render(self):
        if 'excelexport.policy' not in self.request.form:
            self.request.form['excelexport.policy'] = RESTAPI_POLICY
        return self.context.restrictedTraverse('@@collective.excelexportcsv')()


class RestApiSearchDataSource(BaseContentsDataSource):
    """Export the contents of a catalog search
    """
    adapts(Interface, Interface)

    def get_filename(self):
        return "%s" % (
            datetime.datetime.now().strftime("%d-%m-%Y"))

    def _parse_query(self, query):
        catalog_compatible_query = getMultiAdapter(
            (self.context, self.request), IZCatalogCompatibleQuery)(query)
        return catalog_compatible_query

    def _constrain_query_by_path(self, query):
        if 'path' not in query:
            query['path'] = {}

        if isinstance(query['path'], dict) and 'query' not in query['path']:
            path = '/'.join(self.context.getPhysicalPath())
            query['path']['query'] = path

    def get_objects(self):
        query = deepcopy(self.request.form)
        query.pop('excelexport.policy', None)
        query = unflatten_dotted_dict(query)
        query = self._parse_query(query)
        self._constrain_query_by_path(query)
        catalog = api.portal.get_tool('portal_catalog')
        return (b.getObject() for b in catalog.searchResults(**query))
