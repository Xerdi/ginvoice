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

import sys, os
from ginvoice.environment import get_resource


def __safe_path__(filename, default_path):
    if sys.argv[0].endswith('.py'):
        return os.path.join(default_path, filename)
    return get_resource(filename)


def find_css_file(filename):
    return __safe_path__(filename, "../res/css")


def find_ui_file(filename):
    return __safe_path__(filename, "../res/glade")
