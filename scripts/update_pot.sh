#!/bin/bash

PROJECT_DIRECTORY="$(git rev-parse --show-toplevel)"

set -e

cd "$PROJECT_DIRECTORY/res"

UI_FILES=$(ls glade | grep -e '.glade$')
UI_H_FILES=

PY_FILES=$(find ../ginvoice/ -type f -name "*.py" -exec grep -le "from ginvoice.i18n import .*_.*" {} +)
PY_STR=

for ui_file in $UI_FILES; do
  intltool-extract --type="gettext/glade" "./glade/$ui_file"
  UI_H_FILES="$UI_H_FILES ./glade/$ui_file.h"
done

for py_file in $PY_FILES; do
  PY_STR="$PY_STR $py_file"
done

# Create .pot file
# shellcheck disable=SC2086
xgettext -k=_ -kN_ -jo po/ginvoice.pot \
         --from-code utf-8 \
         --copyright-holder='Erik Nijenhuis <erik@xerdi.com>' \
         --package-name='GinVoice' \
         --package-version=0.2 \
         ${PY_STR} \
         ${UI_H_FILES}

# Fix the header
sed -i 's/SOME DESCRIPTIVE TITLE./GinVoice - Creating LaTeX invoices with a GTK GUI/' po/ginvoice.pot

# Add the po file
cd po
msginit -o en.po -i ginvoice.pot --no-translator
msgmerge --update nl.po ginvoice.pot
