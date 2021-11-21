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

import os, gi

from ginvoice.i18n import _
from ginvoice.environment import customer_info_file, supplier_info_file
from ginvoice.model.column import TableColumnStore, CumulativeColumnStore
from ginvoice.model.customer import Customer
from ginvoice.model.info import GenericInfoStore
from ginvoice.model.preference import preference_store
from ginvoice.model.style import Style
from ginvoice.ui.preferences import PreferencesWindow
from ginvoice.util import find_ui_file, find_css_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject


@Gtk.Template.from_file(find_ui_file("invoice.glade"))
class InvoiceForm(Gtk.Box):
    __gtype_name__ = "invoice"

    title = Gtk.Template.Child('title')
    subtitle = Gtk.Template.Child('subtitle')

    addressline1 = Gtk.Template.Child('addressline1')
    addressline2 = Gtk.Template.Child('addressline2')
    addressline3 = Gtk.Template.Child('addressline3')

    customer_info = Gtk.Template.Child('customer_info')
    supplier_info = Gtk.Template.Child('supplier_info')

    invoice_records = Gtk.Template.Child('invoice_records')

    invoice_ending = Gtk.Template.Child('invoice_ending')

    table_column_store = TableColumnStore()
    cumulative_column_store = CumulativeColumnStore()

    def __init__(self, parent: Gtk.Window, invoice_stack: Gtk.Stack, customer: Customer, idx: int):
        super().__init__()
        self.vars = {
            _('invoice_nr'): str(int(preference_store['invoice_counter'].value) + idx),
            _('today'): "{%s}" % _('today')
        }
        self.parent = parent
        self.invoice_stack = invoice_stack
        self.idx = idx
        self.customer = customer
        self.customer.connect('changed', self.update_customer)
        self.title.set_text(preference_store['title'].value)
        preference_store['title'].connect('changed', self.set_title)
        self.subtitle.set_text(preference_store['subtitle'].value)
        preference_store['subtitle'].connect('changed', self.set_subtitle)
        self.customer_info_store = GenericInfoStore(customer_info_file, self.vars)
        self.supplier_info_store = GenericInfoStore(supplier_info_file, self.vars)
        self.customer_info.set_model(self.customer_info_store)
        self.supplier_info.set_model(self.supplier_info_store)
        self.update_customer(customer)
        self.invoice_ending.set_text(preference_store['invoice_ending'].value)
        preference_store['invoice_ending'].connect('changed', self.set_invoice_ending)

    def update_customer(self, customer: Customer):
        self.vars[_('customer_nr')] = str(customer.id)
        self.vars[_('customer_name')] = customer.name
        self.invalidate()

    def set_title(self, preference, title):
        self.title.set_text(title)
        self.vars[_('title')] = title

    def set_subtitle(self, preference, subtitle):
        self.subtitle.set_text(subtitle)
        self.vars[_('subtitle')] = subtitle

    @Gtk.Template.Callback()
    def remove_invoice(self, invoice):
        self.invoice_stack.remove(invoice)

    def set_idx(self, idx: int):
        self.idx = idx
        self.vars[_('invoice_nr')] = str(int(preference_store['invoice_counter'].value) + idx)
        self.invalidate()

    def set_customer(self, customer: Customer):
        self.customer.disconnect_by_func(self.update_customer)
        self.customer = customer
        self.customer.connect('changed', self.update_customer)
        self.update_customer(self.customer)

    @Gtk.Template.Callback()
    def open_document_preferences(self, btn):
        window = PreferencesWindow(section='document_settings')
        window.set_transient_for(self.parent)
        window.show_all()

    @Gtk.Template.Callback()
    def open_info_preferences(self, btn):
        window = PreferencesWindow(section='info')
        window.set_transient_for(self.parent)
        window.show_all()

    @Gtk.Template.Callback()
    def open_table_preferences(self, btn):
        window = PreferencesWindow(section='table_config')
        window.set_transient_for(self.parent)
        window.show_all()

    def set_invoice_ending(self, preference, invoice_ending):
        self.invoice_ending.set_text(invoice_ending)

    def invalidate(self):
        a1, a2, a3 = self.customer.addresslines.split(os.linesep)
        self.addressline1.set_text(a1)
        self.addressline2.set_text(a2)
        self.addressline3.set_text(a3)
        self.customer_info_store.load()
        self.supplier_info_store.load()
        self.table_column_store.load()
        self.cumulative_column_store.load()
        for col_idx, column in enumerate(self.table_column_store):
            col = self.invoice_records.get_column(col_idx)
            col.set_title(column.title)
            if column.size_type == 0:
                col.set_visible(False)
            elif column.size_type == 1:
                col.set_sizing(1)
            elif column.size_type == 2:
                col.set_sizing(0)
        for col_idx, column in enumerate(self.cumulative_column_store):
            print(col_idx, column)


if __name__ == '__main__':
    Style()
    window = Gtk.Window()
    window.add(InvoiceForm())
    window.connect('destroy', Gtk.main_quit)
    window.show_all()
    Gtk.main()
