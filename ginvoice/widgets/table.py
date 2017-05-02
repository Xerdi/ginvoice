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

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ginvoice.i18n import _

columns = [_("Type"), _("Client"), _("Date"), _("Description"), _("Value")]


class Table(Gtk.ScrolledWindow):

    def __init__(self) -> None:
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.record_store = Gtk.ListStore(str, str, str, str, str)
        wrapper = Gtk.Box()
        self.table = Gtk.TreeView(model=self.record_store)
        self.table.set_reorderable(True)
        for idx, col in enumerate(columns):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col, renderer, text=idx)
            column.set_min_width(100)
            self.table.append_column(column)
        wrapper.set_center_widget(self.table)
        self.add(wrapper)

    def add_record(self, record_type, client, date, description, amount):
        self.record_store.append(row=[
            record_type,
            client,
            date,
            description,
            amount
        ])

    def new_record(self):
        last_record = self.record_store.append(row=[_("Minutes"), "", "", "", ""])
        selection = self.table.get_selection()
        selection.select_iter(last_record)

    def clear(self):
        self.record_store.clear()


if __name__ == '__main__':
    window = Gtk.Window()
    window.set_default_size(400, 300)
    window.connect("destroy", Gtk.main_quit)

    table = Table()
    for idx in range(0, 30):
        table.add_record("Dienst", "Client A", "22 feb", "Dingen", "90")

    window.add(table)
    window.show_all()
    Gtk.main()
