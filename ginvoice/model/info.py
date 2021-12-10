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

import os, json, gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk


class GenericInfoStore(Gtk.ListStore):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    data_file = GObject.Property(type=str)

    def __init__(self, data_file, vars=None):
        Gtk.ListStore.__init__(self, str, str)
        self.data_file = data_file
        self.vars = vars

    def load(self):
        self.clear()
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for raw in data:
                    value = raw['val'].format_map(self.vars) if self.vars else raw['val']
                    self.append((raw['key'], value))

    def commit(self):
        with open(self.data_file, 'w') as f:
            json.dump([{'key': c[0], 'val': c[1]} for c in self], f)


