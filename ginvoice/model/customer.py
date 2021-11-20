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

import json

import gi

from ginvoice.environment import customer_file

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gio


class Customer(GObject.GObject):
    __gsignals__ = {
        'created': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'changed': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    id = GObject.Property(type=int)
    name = GObject.Property(type=str)
    addresslines = GObject.Property(type=str)

    def __init__(self):
        GObject.GObject.__init__(self)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'addresslines': self.addresslines
        }


class CustomerStore(Gio.ListStore):
    data_file = GObject.Property(type=str, default=customer_file)

    def __init__(self) -> None:
        super().__init__()

    def load(self):
        self.remove_all()
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            for raw in data:
                customer = Customer()
                customer.id = raw['id']
                customer.name = raw['name']
                customer.addresslines = raw['addresslines']
                self.append(customer)

    def commit(self):
        with open(self.data_file, 'w') as f:
            json.dump([c.to_dict() for c in self], f)
