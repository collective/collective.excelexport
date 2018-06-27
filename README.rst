======================
collective.excelexport
======================

What does this product
======================

This product provides tools to provide excel exports to Plone users,
under xls or csv format.

A framework, with default utilities to export the dexterity contents of a folder,
the results of a catalog search,
and the results of a eea faceted navigation search.
Many field types are managed (text, list, file, boolean, datagrid...).

Try @@collective.excelexport view on any folder containing dexterity elements.
Try @@collective.excelexport?excelexport.policy=excelexport.search&review_state=published on site root.

Try @@collective.excelexportcsv view on any folder for csv export.


How to extend it
================

Datasources
-----------

If you want to implement a new way to get content to export,
you can register a #datasource#,
wich is an adapter for collective.excelexport.interfaces.IDataSource interface.

This adapter can be a named one.

You will call this datasource calling the view @@collective.excelexport?excelexport.policy=datasourcename

See the IDataSource interface for more information



Exportables (excel sheet columns)
---------------------------------

If you want to define new columns for your excel export, you will write or override: ::

  - Exportable factories, adapters for IExportableFactory interface that provides a list of Exportables
  - Exportables, that define columns.

Example of an exportable factory: ::

    from plone.dexterity.interfaces import IDexterityFTI
    from collective.excelexport.exportables.base import BaseExportableFactory
    from collective.excelexport.exportables.dexterityfields import get_ordered_fields
    from collective.excelexport.exportables.dexterityfields import get_exportable
    from collective.excelexport.exportables.dexterityfields import ParentField
    from collective.excelexport.exportables.dexterityfields import GrandParentField

    class PSTActionFieldsFactory(BaseExportableFactory):
        adapts(IDexterityFTI, Interface, Interface)
        portal_types = ('pstaction',)

        def get_exportables(self):
            portal_types = api.portal.get_tool('portal_types')
            action_fti = portal_types['pstaction']
            oo_fti = portal_types['operationalobjective']
            os_fti = portal_types['strategicobjective']
            fields = []
            fields.extend([get_exportable(
                field[1], self.context, self.request)
                for field in get_ordered_fields(action_fti)])
            fields.extend([get_exportable(
                ParentField(field[1]), self.context, self.request)
                for field in get_ordered_fields(oo_fti)])
            fields.extend([get_exportable(
                GrandParentField(field[1]), self.context, self.request)
                for field in get_ordered_fields(os_fti)])
            return fields


Dexterity exportables
---------------------

You have a complete set of exportables for dexterity fields.
Those are multi-adapters of field, context and request.

You can override them declaring a more specific adapter.

You can also declare a named adapter with the field name if you want a specific
rendering for one field.


Styles
------

If you don't feel good with default styles, you can register a specific one for: ::
  - the export policy
  - the context
  - the layer

You just have to register a new IStyle adapter, in a zcml: ::

    <adapter for="zope.interface.Interface
                  .interfaces.IThemeSpecific"
             factory=".excelstyles.MyNeutralStyle"
             provides="collective.excelexport.interfaces.IStyles"
              />

If you do not specify the name, the styles will be registered for all policies.

and in python: ::


	class MyNeutralStyle(Styles):

	    content = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold off; '
	                     'align: wrap off, vert centre, horiz left;'
	                     'borders: top thin, bottom thin, left thin, right thin;'
	                     'pattern: pattern solid, back_colour white, fore_colour white'
	                     )

	    headers = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; '
	                         'align: wrap off, vert centre, horiz left; '
	                         'borders: top thin, bottom thin, left thin, right thin; '
	                         'pattern: pattern solid, back_colour white, fore_colour white; '
	                         )

plone.restapi
=============

To get an export via rest api, query @collective.excelexport / @collective.excelexportcsv (with one @)


Tests
=====

This add-on is tested using Travis CI. The current status of the add-on is :

.. image:: https://secure.travis-ci.org/collective/collective.excelexport.png
    :target: http://travis-ci.org/collective/collective.excelexport

.. image:: https://coveralls.io/repos/collective/collective.excelexport/badge.png?branch=master
    :target: https://coveralls.io/r/collective/collective.excelexport?branch=master
