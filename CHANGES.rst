Changelog
=========


1.7 (2018-06-22)
----------------

- Added plone.restapi service.
  [thomasdesvenain]

- Fixed csv export mimetype.

- Added helper method get_exportable_for_fieldname.
  [gbastien]

1.6 (2018-01-05)
----------------

- Fix: no limit for number of results in eeafaceted datasource.
  [cedricmessiant]

1.5 (2017-11-28)
----------------

- Upgrade bootstrap.
  [sgeulette]
- Fix: render choice field with source vocabulary
  [sgeulette]

1.4 (2017-05-31)
----------------

- Prevent removal of exportables with similar names when ordering them
  [thomasdesvenain]
- Refactor: view exposes method that creates data buffer from sheet data.
  [thomasdesvenain]
- Made correct release
  [sgeulette]

1.3 (2016-11-28)
----------------

- Fix: check if value_type is empty for collection field render.
  [bsuttor]

- Fix: try to get the value of a method if the field is a method and translate
  DateTime results to a unicode, this fixes the export for objects with the IPublication
  Behavior.
  [pcdummy]

- Fix: be sure to not retrieve an attribute on an object by acquisition.
  [vincentfretin]

- Feature: render_style can now return a Style object with content and headers
  attribute to be able to customise the header style per exportable.
  [vincentfretin]

- Feature: the passed obj to render_value is now
  exportable.field.bind(obj).context to make it easier to get data from
  parent or grandparent.
  [vincentfretin]

- Feature: BaseFieldRenderer.render_header method returns now the translated field
  title instead of the Message object.
  [vincentfretin]

- Fix: Ignore reverse parameter when creating export url.
  [cedricmessiant]

- Feature: Add sort exportables feature using exportables_order list.
  Works with field and non-field exportables.
  [cedricmessiant, ebrehault, thomasdevenain]

1.2 (2014-09-10)
----------------

- Feature: Added export under csv format.
  [thomasdesvenain]

- API: Filter exportables by field name by default using excluded_exportables list.
  [cedricmessiant]

- API: We can define a dexterity adapter for just one field using field name as
  adapter name.
  [thomasdesvenain]

- Fix: Faceted nav export link ignores results per page criterion.
  [thomasdesvenain]

- Fix: Translate sheet title.
  [thomasdesvenain]

- Fix: Improve text fields support.
  [fngaha, thomasdesvenain]

1.1 (2014-06-19)
----------------

- Rename search policy excelexport.search to avoid conflict with 'search' view.
  [thomasdesvenain]


1.0 (2014-06-02)
----------------

- Initial release.
  [thomasdesvenain]
