from copy import deepcopy

from zope.interface import Interface
from zope.component import adapts
from datetime import datetime

from plone import api
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from collective.excelexport.datasources.base import BaseContentsDataSource


class SearchContentsDataSource(BaseContentsDataSource):
    """Export the contents of a catalog search
    """
    adapts(IPloneSiteRoot, Interface)

    def get_filename(self):
        return "%s" % (
                datetime.now().strftime("%d-%m-%Y"))

    def get_objects(self):
        query = deepcopy(self.request.form)
        query.pop('excelexport.policy', None)
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(**query)
        return [b.getObject() for b in brains]
