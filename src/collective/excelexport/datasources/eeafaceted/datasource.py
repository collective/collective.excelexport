from datetime import datetime
from copy import copy

from zope.component import adapts
from zope.interface import Interface

from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable

from collective.excelexport.datasources.base import BaseContentsDataSource


class FacetedSearchDataSource(BaseContentsDataSource):
    adapts(IFacetedNavigable, Interface)

    def get_filename(self):
        return "%s-%s-search.xls" % (
                datetime.now().strftime("%d-%m-%Y"), self.context.getId())

    def get_objects(self):
        faceted_query_view = self.context.unrestrictedTraverse('@@faceted_query')
        params = copy(self.request.form)
        if 'excelexport.policy' in params:
            del params['excelexport.policy']

        brains = faceted_query_view.query(**params)
        return [b.getObject() for b in brains._sequence]
