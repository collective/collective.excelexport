def upgrade_to_2(context):
    context.runImportStepFromProfile('collective.excelexport:default', 'plone.app.registry')
