#!/bin/bash
# GinVoice - Creating LaTeX invoices with a GTK GUI
# Copyright (C) 2021  Erik Nijenhuis <erik@xerdi.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
         --copyright-holder='Xerdi' \
         --package-name='GinVoice' \
         --package-version=$(git describe --tags) \
         ${PY_STR} \
         ${UI_H_FILES}

# Fix the header
sed -i 's/SOME DESCRIPTIVE TITLE./GinVoice - Creating LaTeX invoices with a GTK GUI/' po/ginvoice.pot

# Add the po file
cd po
msginit -o en.po -i ginvoice.pot --no-translator
msgmerge --update nl.po ginvoice.pot
