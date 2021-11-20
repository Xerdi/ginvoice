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

import os.path

import gi, json

from ginvoice.environment import customer_file, table_column_file, cumulative_column_file

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Gio


class Column(GObject.GObject):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    title = GObject.Property(type=str, default='')
    size_type = GObject.Property(type=int, default=-1)
    text = GObject.Property(type=str, default='')

    def __init__(self):
        GObject.GObject.__init__(self)

    def to_dict(self):
        return {
            'title': self.title,
            'size_type': self.size_type,
            'text': self.text
        }


class TableColumnHandler(GObject.GObject):

    title = GObject.Property(type=Gtk.Entry)
    stype = GObject.Property(type=Gtk.ComboBox)
    text = GObject.Property(type=Gtk.Entry)
    data = GObject.Property(type=Column)

    def __init__(self, title, stype, text, data):
        GObject.GObject.__init__(self)
        self.title = title
        self.title.set_text(data.title)
        self.stype = stype
        self.stype.set_active(data.size_type)
        self.text = text
        self.text.set_text(data.text)
        self.data = data
        self.title.connect('changed', self.title_changed)
        self.stype.connect('changed', self.stype_changed)
        self.text.connect('changed', self.text_changed)

    def title_changed(self, entry):
        self.data.title = entry.get_text()

    def stype_changed(self, combobox):
        stype = self.data.stype = combobox.get_model()[combobox.get_active_iter()][0]
        if stype == 2:
            self.text.set_text(self.data.text or '')
            self.text.set_sensitive(True)
        else:
            self.text.set_text('')
            self.text.set_sensitive(False)

    def text_changed(self, entry):
        self.data.text = entry.get_text()


class TableColumnStore(Gio.ListStore):
    data_file = GObject.Property(type=str, default=table_column_file)

    def __init__(self) -> None:
        super().__init__()

    def load(self):
        self.remove_all()
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for raw in data:
                    column = Column()
                    column.title = raw['title']
                    column.size_type = int(raw['size_type'])
                    column.text = raw['text'] if 'text' in raw else ''
                    self.append(column)

    def commit(self):
        with open(self.data_file, 'w') as f:
            json.dump([c.to_dict() for c in self], f)


class CumulativeColumnStore(TableColumnStore):

    def __init__(self):
        super().__init__()
        self.data_file = cumulative_column_file

