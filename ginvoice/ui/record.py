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

from ginvoice.model.record import Record
from ginvoice.util import find_ui_file
from ginvoice.i18n import _

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@Gtk.Template.from_file(find_ui_file("record.glade"))
class RecordDialog(Gtk.Window):

    __gtype_name__ = "record_dialog"

    repeat = Gtk.Template.Child('repeat_checkbox')
    description = Gtk.Template.Child()
    date = Gtk.Template.Child()
    quantity = Gtk.Template.Child()
    price = Gtk.Template.Child()
    discount = Gtk.Template.Child()
    vat = Gtk.Template.Child()

    vat_store = Gtk.Template.Child()

    units_radio = Gtk.Template.Child()
    hours_radio = Gtk.Template.Child()
    minutes_radio = Gtk.Template.Child()

    percentages_radio = Gtk.Template.Child()
    fixed_radio = Gtk.Template.Child()

    def __init__(self, event):
        super().__init__()
        self.event = event

    @Gtk.Template.Callback()
    def save(self, btn):
        record = Record()
        record.description = self.description.get_text()
        record.date = self.date.get_text()
        qtype = self.quantity_type()
        if qtype == 0:
            record.quantity_postfix = _('x')
        elif qtype == 1:
            record.quantity_postfix = _('h')
        elif qtype == 2:
            record.quantity_postfix = _('m')
        record.quantity = int(self.quantity.get_text()) if qtype == 0 else float(self.quantity.get_text())
        record.price = float(self.price.get_text())
        if self.percentages_radio.get_active():
            record.discount = record.quantity * record.price * (int(self.discount.get_text()) / 100)
        else:
            record.discount = float(self.discount.get_text())

        subtotal, vat, total = self.calc_record(
            record.quantity * 60 if qtype == 1 else record.quantity,
            record.price / 60.0 if qtype == 1 else record.price,
            record.discount,
            self.vat_store[self.vat.get_active()][0]
        )

        record.subtotal = subtotal
        record.vat = vat
        record.total = total
        self.event.emit('saved', record)
        if not self.repeat.get_active():
            self.destroy()

    def calc_record(self, quantity, price, discount, vat_percent):
        subtotal = quantity * price - discount
        vat_multiplier = vat_percent / 100
        vat = round(subtotal * vat_multiplier, 2)
        total = subtotal + vat
        return subtotal, vat, total

    def quantity_type(self):
        for i, x in enumerate([self.units_radio, self.hours_radio, self.minutes_radio]):
            if x.get_active():
                return i
        return -1

    @Gtk.Template.Callback()
    def close(self, btn):
        self.destroy()
