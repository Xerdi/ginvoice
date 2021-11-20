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

from ginvoice.model.info import GenericInfoStore
from ginvoice.ui import variable
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@Gtk.Template.from_file(find_ui_file("info.glade"))
class InfoWindow(Gtk.Window):
    __gtype_name__ = "info_dialog"

    title = Gtk.Template.Child('title')
    value = Gtk.Template.Child('value')
    repeat = Gtk.Template.Child('repeat_checkbox')

    def __init__(self, title: str, store: GenericInfoStore, iter=None):
        Gtk.Window.__init__(self)
        self.set_title(title)
        self.store = store
        self.iter = iter
        if iter:
            self.repeat.set_no_show_all(True)
            self.repeat.set_visible(False)
            self.title.set_text(self.store[iter][0])
            self.value.set_text(self.store[iter][1])

    @Gtk.Template.Callback()
    def save(self, btn):
        if self.iter:
            self.store.set_value(self.iter, 0, self.title.get_text())
            self.store.set_value(self.iter, 1, self.value.get_text())
        else:
            self.store.append((self.title.get_text(), self.value.get_text()))
        if self.repeat.get_active():
            self.title.set_text('')
            self.value.set_text('')
            self.title.grab_focus()
        else:
            self.destroy()

    @Gtk.Template.Callback()
    def close(self, btn):
        self.destroy()
