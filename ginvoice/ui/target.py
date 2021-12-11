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
from ginvoice.model.preference import preference_store

from ginvoice.i18n import _
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


@Gtk.Template.from_file(find_ui_file("target.glade"))
class TargetChooserDialog(Gtk.FileChooserDialog):
    __gtype_name__ = "target_chooser"

    def __init__(self, default_filename=_('Invoice')):
        Gtk.FileChooserDialog.__init__(self)
        self.set_action(Gtk.FileChooserAction.SAVE)
        self.set_current_name(default_filename)
        if preference_store['target_directory'].value:
            self.set_current_folder(preference_store['target_directory'].value)
