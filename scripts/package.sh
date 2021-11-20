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

set -e

cd "$PROJECT_DIRECTORY/res/basic_template"
latexmk -C
rm -f footer.tex header.tex languages.tex meta.tex style.tex table.tex

cd ..
tar -zcvf basic_template.tar.gz basic_template

cd "$PROJECT_DIRECTORY"

debuild -us -uc

cd debian
dpkg-deb --build "$TARGET"
