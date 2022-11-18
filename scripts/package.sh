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

TARGET="${1:-ginvoice}"
PROJECT_DIRECTORY="$(git rev-parse --show-toplevel)"
export DH_VERBOSE=1

set -e

cd "$PROJECT_DIRECTORY/res/basic_template"

echo "Cleaning up the template directory"
latexmk -C &> /dev/null
rm -f languages.tex\
  header.tex\
  addressee.tex\
  customer_info.tex\
  supplier_info.tex\
  table.tex\
  footer.tex\
  style.tex\
  meta.tex

cd ..
echo "Creating template tarball"
tar -zcvf basic_template.tar.gz basic_template

cd "$PROJECT_DIRECTORY"

scripts/show_changelog.sh > debian/changelog

echo "Creating .deb package"
dpkg-buildpackage -kerik@xerdi.com
#dpkg-buildpackage -us -uc

cd debian
dpkg-deb --build "$TARGET"
