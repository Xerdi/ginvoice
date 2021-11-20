#!/bin/bash

PROJECT_DIRECTORY="$(git rev-parse --show-toplevel)"

set -e

cd "$PROJECT_DIRECTORY/res"

UI_FILES="app.glade customer.glade invoice.glade preferences.glade"
UI_H_FILES=

for ui_file in $UI_FILES; do
  intltool-extract --type="gettext/glade" "./glade/$ui_file"
  UI_H_FILES="$UI_H_FILES ./glade/$ui_file.h"
done

# Create .pot file
# shellcheck disable=SC2086
xgettext -k=_ -kN_ -jo po/ginvoice.pot \
         --from-code utf-8 \
         --copyright-holder='Erik Nijenhuis <erik@xerdi.com>' \
         --package-name='GinVoice' \
         --package-version=0.2 \
         ../ginvoice/main.py \
         ../ginvoice/ui/customer.py \
         ../ginvoice/ui/invoice.py \
         ../ginvoice/ui/preferences.py \
         ${UI_H_FILES}

# Fix the header
sed -i 's/SOME DESCRIPTIVE TITLE./GinVoice - Creating LaTeX invoices with a GTK GUI/' po/ginvoice.pot

# Add the po file
cd po
msginit -o en.po -i ginvoice.pot --no-translator
msgmerge --update nl.po ginvoice.pot
