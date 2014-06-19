======================
collective.excelexport
======================

What does this product
======================

This product provides tools to provide excel exports to Plone users.

A framework, with default utilities to export the dexterity contents of a folder,
the results of a catalog search,
and the results of a eea faceted navigation search.
Many field types are managed (text, list, file, boolean, datagrid...).

Try @@collective.excelexport view on any folder containing dexterity elements.
Try @@collective.excelexport?export.policy=excelexport.search&review_state=published on site root.


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


Tests
=====

This add-on is tested using Travis CI. The current status of the add-on is :

.. image:: https://secure.travis-ci.org/collective/collective.excelexport.png
    :target: http://travis-ci.org/collective/collective.excelexport
