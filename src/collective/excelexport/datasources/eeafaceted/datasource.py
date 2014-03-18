from datetime import datetime
from copy import copy

from collective.excelexport.datasources.folder import BaseContentsDataSource


class FacetedSearchDataSource(BaseContentsDataSource):

    def get_filename(self):
        return "%s-%s-search.xls" % (
                datetime.now().strftime("%d-%m-%Y"), self.context.getId())

    def get_objects(self):
        faceted_query_view = self.context.unrestrictedTraverse('@@faceted_query')
        params = copy(self.request.form)
        if 'excelexport.policy' in params:
            del params['excelexport.policy']
        #@TODO: check this is not batched
        brains = faceted_query_view.query(**params)
        return [b.getObject() for b in brains]
