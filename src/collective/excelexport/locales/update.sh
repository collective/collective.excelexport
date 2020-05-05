#!/bin/bash

DOMAIN="collective.excelexport"
I18NDUDE=i18ndude
FINDPATH=..
FINDUNTRANSLATED=`find \$FINDPATH/ -name '*pt'`

# Synchronise the .pot with the templates.
$I18NDUDE rebuild-pot \
          --pot $DOMAIN.pot \
          --create $DOMAIN \
          $FINDPATH/
$I18NDUDE rebuild-pot \
          --pot plone.pot \
          --create plone \
          $FINDPATH/profiles/default

# Synchronise the resulting .pot with the .po files
$I18NDUDE sync \
          --pot $DOMAIN.pot \
          */LC_MESSAGES/$DOMAIN.po
$I18NDUDE sync \
          --pot plone.pot \
          */LC_MESSAGES/plone.po

WARNINGS=`$FINDUNTRANSLATED | xargs \$I18NDUDE find-untranslated | grep -e '^-WARN' | wc -l`
ERRORS=`$FINDUNTRANSLATED | xargs \$I18NDUDE find-untranslated | grep -e '^-ERROR' | wc -l`
FATAL=`$FINDUNTRANSLATED  | xargs \$I18NDUDE find-untranslated | grep -e '^-FATAL' | wc -l`

echo ""
echo "There are $WARNINGS warnings (possibly missing i18n markup)"
echo "There are $ERRORS errors (almost definitely missing i18n markup)"
echo "There are $FATAL fatal errors (template could not be parsed, eg. if it's not html)"

if [ -e $PWD/rebuild_i18n.log ]
then
    echo ""
    echo "Removing previous report for untranslated strings..."
    rm $PWD/rebuild_i18n.log
    echo "Adding a details report for untranslated strings..."
    touch $PWD/rebuild_i18n.log
    $FINDUNTRANSLATED | xargs $I18NDUDE find-untranslated > $PWD/rebuild_i18n.log
else
    echo ""
    echo "Adding a details report for untranslated strings..."
    touch $PWD/rebuild_i18n.log
    $FINDUNTRANSLATED | xargs $I18NDUDE find-untranslated > $PWD/rebuild_i18n.log
fi

echo ""
echo "For more details, run 'find $FINDPATH/ -name \"*pt\" | xargs $I18NDUDE find-untranslated' or"
echo "Look the rebuild i18n log generate for this script called 'rebuild_i18n.log' on locales dir"
# Ok, now your gettext files editor favorite is your friend!
