======================
collective.excelexport
======================

What does this product
======================

This product provides tools to provide excel exports to `Plone`_ users,
under xls or csv format.

A framework, with default utilities to export the dexterity contents of a folder,
the results of a catalog search,
and the results of a `eea faceted navigation`_ search.
Many field types are managed (text, list, file, boolean, datagrid...).

Try @@collective.excelexport view on any folder containing dexterity elements.
Try @@collective.excelexport?excelexport.policy=excelexport.search&review_state=published on site root.

Try @@collective.excelexportcsv view on any folder for csv export.


Translations
============

This product has been translated into

- French.

- Spanish.

You can contribute for any message missing or other new languages, join us at
`Plone Collective Team <https://www.transifex.com/plone/plone-collective/>`_
into *Transifex.net* service with all world Plone translators community.


Installation
============

Install ``collective.excelexport`` by adding it to your buildout:

   [buildout]

    ...

    eggs =
        collective.excelexport


and then running "bin/buildout"


How to configure this product
=============================

You can set a list of fields to be excluded from export via the registry record:
*collective.excelexport.excluded_exportables*


How to extend it
================

Datasources
-----------

If you want to implement a new way to get content to export,
you can register a #datasource#, which is an adapter for
collective.excelexport.interfaces.IDataSource interface.

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

To get an export via `rest api`_, query @collective.excelexport / @collective.excelexportcsv (with one @)


Versions
========

- Version 2.x is for Plone 6+ only
- Version 1.x is for Plone 4 / 5


Tests status
============

This add-on is tested using Github action. The current status of the add-on is:

.. image:: https://github.com/collective/collective.excelexport/actions/workflows/main.yml/badge.svg
    :target: https://github.com/collective/collective.excelexport/actions/workflows/main.yml

.. image:: https://coveralls.io/repos/github/collective/collective.excelexport/badge.svg
    :target: https://coveralls.io/github/collective/collective.excelexport

.. image:: http://img.shields.io/pypi/v/collective.excelexport.svg
   :alt: PyPI badge
   :target: https://pypi.org/project/collective.excelexport


Contribute
==========

Have an idea? Found a bug? Let us know by `opening a ticket`_.

- Issue Tracker: https://github.com/collective/collective.excelexport/issues
- Source Code: https://github.com/collective/collective.excelexport


License
=======

The project is licensed under the GPLv2.

.. _Plone: https://plone.org/
.. _`eea faceted navigation`: http://eea.github.io/docs/eea.facetednavigation/index.html
.. _`rest api`: https://pypi.org/project/plone.restapi/
.. _`opening a ticket`: https://github.com/collective/collective.excelexport/issues
