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

import sys

from ginvoice.gtk import Gtk, Gio
from ginvoice.environment import setup_environment
from ginvoice.ui.app import GinVoiceWindow


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.xerdi.ginvoice",
                         flags=Gio.ApplicationFlags.FLAGS_NONE, **kwargs)
        self.window = None

    def do_activate(self):
        self.window = self.window or GinVoiceWindow(application=self)
        self.window.present()


def main():
    setup_environment()
    Application().run(sys.argv)


if __name__ == '__main__':
    main()
