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
    exportables_order = Attribute("""List of exportable names by order of appareance in the export table.
    The names are the field names and/or the names of the exportable classes.
    """)
    excluded_exportables = Attribute("""List of exportables excluded from this source.
    The names are the field names and/or the names of the exportable classes.
    """)
    excluded_factories = Attribute("""List of exportable factories excluded from this source.
    The names are the IExportableFactory utility names.
    """)

    def get_filename(self):
        """Gets the file name (without extension) of the exported excel
        """

    def get_sheets_data(self):
        """Gets a list of dictionaries with three keys :
            title: the title of the sheet
            objects: the list of objects
            exportables: the names of the exportables to render
        """


class IStyles(Interface):
    """Get the style of header and content cells
    provided by a named adapter that adapts the context and the request
    """

    heading = Attribute("""xlwt Style object for column headers""")
    content = Attribute("""xlwt Style object for contents""")


class IExportableFactory(Interface):
    """Adapter to get exportables (ex: fields, history, etc)
    we can have many exportable factories for a fti
    we can restrict an exportable factory on few portal types or behaviors
    """
    portal_types = Attribute("""list: portal_types on wich this factory applies""")
    behaviors = Attribute("""list of interfaces: if set, the factory applies on types implementing one of those behaviors""")
    weight = Attribute("""Weight for order (the lower, the first)""")

    def get_exportables(self):
        """List of exportables for the content type
        """


class IExportable(Interface):
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
