# GinVoice - Creating LaTeX invoices with a GTK GUI
# Copyright (C) 2024  Erik Nijenhuis <erik@xerdi.com>
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

from ginvoice.util import find_logo_file
from ginvoice.gtk import Gtk
from ginvoice.i18n import _


class AboutDialog(Gtk.AboutDialog):

    __gtype_name__ = "about_dialog"

    def __init__(self, *args, **kwargs):
        Gtk.AboutDialog.__init__(self, *args, **kwargs)
        image = Gtk.Image.new_from_file(find_logo_file("ginvoice.png"))
        self.set_program_name("GinVoice")
        self.set_version("1.0.4")
        self.set_comments(_("Creating LaTeX invoices with a GTK GUI"))
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_logo(image.get_pixbuf())
        self.set_authors(["Erik Nijenhuis <erik@xerdi.com>"])
        self.set_copyright("Copyright \xa9 Xerdi")
        self.set_website("https://gitlab.gnome.org/MacLotsen/ginvoice")
        self.set_website_label("GNOME GitLab")
