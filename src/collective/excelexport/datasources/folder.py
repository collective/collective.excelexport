from datetime import datetime

from Products.CMFCore.interfaces import IFolderish
from collective.excelexport.datasources.base import BaseContentsDataSource
from plone import api
from zope.component import adapts
from zope.interface import Interface


class FolderContentsDataSource(BaseContentsDataSource):
    """Export the contents of a folder
    """
    adapts(IFolderish, Interface)

    def get_filename(self):
        return "%s-%s" % (
            datetime.now().strftime("%d-%m-%Y"),
            self.context.getId(),
        )

    def get_objects(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.searchResults(
            REQUEST=self.request,
            path={'query': '/'.join(self.context.getPhysicalPath()),
                  'depth': 1},
        )
        return [b.getObject() for b in brains]
