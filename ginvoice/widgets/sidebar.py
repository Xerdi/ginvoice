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


class Sidebar(Gtk.Grid):

    def __init__(self, min_width=None) -> None:
        super().__init__()

        self.stack = Gtk.Stack()
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        self.attach(self.stack, 1, 0, 1, 1)

        self.stack_sidebar = Gtk.StackSidebar()
        if min_width:
            self.stack_sidebar.set_size_request(min_width, -1)
        self.stack_sidebar.set_stack(self.stack)
        self.attach(self.stack_sidebar, 0, 0, 1, 1)

    def add_titled(self, widget, name, title):
        self.stack.add_titled(widget, name, title if len(title) < 32 else title[:20]+"...")


if __name__ == '__main__':
    window = Gtk.Window()
    window.set_default_size(400, 300)
    window.connect("destroy", Gtk.main_quit)

    sidebar = Sidebar()
    for idx in range(0, 30):
        sidebar.add_titled(Gtk.Label(label="Example %d" % idx), "Example %d" % idx, "Title %d" % idx)

    window.add(sidebar)
    window.show_all()
    Gtk.main()
