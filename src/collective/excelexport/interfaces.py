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

    def get_filename(self):
        """Gets the file name of the exported excel
        """

    def get_sheets_data(self):
        """Gets a list of dictionaries with three keys :
            title: the title of the sheet
            objects: the list of objects
            fields: the fields to render
        """


class IStyles(Interface):
    """Get the style of header and content cells
    provided by a named adapter that adapts the context and the request
    """

    heading = Attribute("""xlwt Style object for column headers""")
    content = Attribute("""xlwt Style object for contents""")


class IFieldsFactory(Interface):
    """Adapter to get fields
    we can have many fields factories for a fti
    we can restrict a field factory to few portal types or behaviors
    """
    portal_types = Attribute("""list: portal_types on wich this factory applies""")
    behaviors = Attribute("""list of interfaces: if set, the factory applies on types implementing one of those behaviors""")
    weight = Attribute("""Weight for order (the lower, the first)""")

    def get_fields(self):
        """List of fields for the content type
        """


class IExcelRenderer(Interface):
    """Render a value and a style from something, for example a field
    """

    def render_header(self):
        """Gets the value to render on the first row of excel sheet for this field
        """

    def render_value(self, obj):
        """Gets the value to render in excel file from content
        """

    def render_style(self, obj, base_style):
        """Gets the style rendering of the
        base_style is the default style of a cell for content
        """
