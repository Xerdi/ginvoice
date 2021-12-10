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
from gi.repository import Gtk, GObject


class Record(GObject.GObject):
    description = GObject.Property(type=str, default='')
    date = GObject.Property(type=str, default='')
    quantity = GObject.Property(type=float, default=0)
    quantity_postfix = GObject.Property(type=str, default='')
    price = GObject.Property(type=float, default=0)
    discount = GObject.Property(type=float, default=0)
    subtotal = GObject.Property(type=float, default=0)
    vat = GObject.Property(type=float, default=0)
    total = GObject.Property(type=float, default=0)

    def as_list(self):
        return [
            self.description,
            self.date,
            self.quantity_format(),
            str(self.price),
            str(self.discount),
            str(self.subtotal),
            str(self.vat),
            str(self.total),
            self,
            1
        ]

    def quantity_format(self):
        return "%g%s" % (self.quantity, self.quantity_postfix)


class RecordEvent(GObject.GObject):
    __gsignals__ = {
        'saved': (GObject.SignalFlags.RUN_FIRST, None, (Record,))
    }

