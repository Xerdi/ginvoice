#!/bin/bash

PROJECT_DIRECTORY="$(git rev-parse --show-toplevel)"

set -e

cd "$PROJECT_DIRECTORY/res"

# Create .pot file
xgettext --language=Python --keyword=_ -jo po/ginvoice.pot \
         --copyright-holder='Erik Nijenhuis <erik@xerdi.com>' \
         --package-name='GinVoice' \
         --package-version=0.1 \
         ginvoice/app.py \
         ginvoice/records.py \
         ginvoice/customers.py \
         ginvoice/widgets/table.py

# Fix the header
sed -i 's/SOME DESCRIPTIVE TITLE./GinVoice - Creating LaTeX invoices with a GTK GUI/' po/ginvoice.pot
