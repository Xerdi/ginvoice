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

from ginvoice.gtk import Gtk, Gdk
from ginvoice.model.preference import preference_store
from ginvoice.util import find_css_file


class Style:
    screen = Gdk.Screen.get_default()
    style_context = Gtk.StyleContext()

    def __init__(self):
        provider = Gtk.CssProvider()
        self.style_context.add_provider_for_screen(
            self.screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        provider.load_from_path(find_css_file('style.css'))
        preference_store['foreground_color'].connect('changed', self.load_css)
        preference_store['background_color'].connect('changed', self.load_css)
        self.load_css()

    def load_css(self, *args):
        provider = Gtk.CssProvider()
        self.style_context.add_provider_for_screen(
            self.screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        provider.load_from_data(
            bytes((".headerfg { color: %s; } .headerbg { background-color: %s; }" %
                   (preference_store['foreground_color'].value, preference_store['background_color'].value)).encode()))
