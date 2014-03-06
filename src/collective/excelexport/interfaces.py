# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface, Attribute
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveExcelexportLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IDataSource(Interface):
    """Gets the fields and objects to serialize in excel file
    provided by a named adapter that adapts the context and the request
    """

    def get_sheets_data(self):
        """Gets a list of dictionaries with three keys :
            title: the title of the sheet
            objects: the list of objects
            fields: the names of the fields to render
        """


class IStyles(Interface):
    """Get the style of header and content cells
    provided by a named adapter that adapts the context and the request
    """

    heading = Attribute("""xlwt Style object for column headers""")
    content = Attribute("""xlwt Style object for contents""")


class IFieldRenderer(Interface):
    """Render a value and a style from a field considering the value
    provided by a named adapter that adapts a field object,
    the export context and the request
    """

    def render_header(self):
        """Gets the value to render on the first row of excel sheet for this field
        """

    def render_value(self, value):
        """Gets the value to render in excel file from content value
        """

    def render_style(self, value, base_style):
        """Gets the style rendering of the
        base_style is the default style of a cell for content
        """


class IValueGetter(Interface):
    """Adapter to get a value from fieldname
    """

    def get(self, fieldname):
        """Get value from fieldname
        """

class IExportablePropertiesFactory(Interface):
    """Named utility to get exportable properties (ex: fields, history, etc)
    """