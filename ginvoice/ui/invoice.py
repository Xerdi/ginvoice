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
import shutil
from subprocess import Popen

from ginvoice.i18n import _
from ginvoice.environment import customer_info_file, supplier_info_file
from ginvoice.model.column import TableColumnStore, CumulativeColumnStore
from ginvoice.model.customer import Customer
from ginvoice.model.form import FormEvent
from ginvoice.model.pdf import PDF
from ginvoice.model.record import RecordEvent, Record
from ginvoice.model.info import GenericInfoStore
from ginvoice.model.preference import preference_store
from ginvoice.model.style import Style
from ginvoice.tex_project import TexProject
from ginvoice.ui.preferences import PreferencesWindow
from ginvoice.ui.record import RecordDialog
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


@Gtk.Template.from_file(find_ui_file("invoice.glade"))
class InvoiceForm(Gtk.Box):
    __gtype_name__ = "invoice"

    title = Gtk.Template.Child()
    subtitle = Gtk.Template.Child()

    address = Gtk.Template.Child()

    customer_info = Gtk.Template.Child()
    supplier_info = Gtk.Template.Child()

    invoice_records = Gtk.Template.Child()
    invoice_row_store = Gtk.Template.Child()
    cumulative_records = Gtk.Template.Child()

    invoice_ending = Gtk.Template.Child()

    table_column_store = TableColumnStore()
    cumulative_column_store = CumulativeColumnStore()
    grand_totals = [0, 0, 0, 0]

    preview_toggle = Gtk.Template.Child()

    def __init__(self, parent: Gtk.Window, invoice_stack: Gtk.Stack, customer: Customer, idx: int,
                 event: FormEvent):
        super().__init__()
        self.tex_project = TexProject()
        self.pdf = PDF(customer,
                       self.table_column_store,
                       self.cumulative_column_store,
                       self.invoice_row_store,
                       self.grand_totals,
                       self.tex_project.working_directory)
        self.event = event
        self.record_event = RecordEvent()
        self.record_event.connect('saved', self.do_add_record)
        self.event.connect('saved', self.invalidate)
        self.address_store = Gtk.ListStore(str)

        self.vars = {
            _('invoice_nr'): str(int(preference_store['invoice_counter'].value) + idx),
            _('today'): "\\today"
        }
        self.reload_cumulatives()
        self.parent = parent
        self.invoice_stack = invoice_stack
        self.idx = idx
        self.customer = customer
        self.customer.connect('changed', self.update_customer)
        self.address.set_model(self.address_store)
        self.title.set_text(preference_store['title'].value)
        preference_store['title'].connect('changed', self.set_title)
        self.subtitle.set_text(preference_store['subtitle'].value)
        preference_store['subtitle'].connect('changed', self.set_subtitle)
        self.customer_info_store = GenericInfoStore(customer_info_file, self.vars)
        self.supplier_info_store = GenericInfoStore(supplier_info_file, self.vars)
        self.customer_info.set_model(self.customer_info_store)
        self.supplier_info.set_model(self.supplier_info_store)
        self.update_customer(customer)
        preference_store['invoice_ending'].connect('changed', self.set_invoice_ending)
        self.invoice_ending.set_text(preference_store['invoice_ending'].value.format_map(self.vars))

    def update_customer(self, customer: Customer):
        self.vars[_('customer_nr')] = customer.id
        self.vars[_('customer_name')] = customer.name
        self.pdf.customer = customer
        self.invalidate()

    def set_title(self, preference, title):
        self.title.set_text(title)
        self.vars[_('title')] = title

    def set_subtitle(self, preference, subtitle):
        self.subtitle.set_text(subtitle)
        self.vars[_('subtitle')] = subtitle

    def do_remove_invoice(self, dialog, response, invoice):
        if response == Gtk.ResponseType.OK:
            self.tex_project.stop_tex()
            self.tex_project.stop_previewer()
            shutil.rmtree(self.tex_project.working_directory, ignore_errors=True)
            self.invoice_stack.remove(invoice)
        if dialog:
            dialog.destroy()

    @Gtk.Template.Callback()
    def remove_invoice(self, invoice):
        if preference_store['show_invoice_removal'].value:
            confirm_dialog = Gtk.MessageDialog(title=_("Delete Invoice Confirmation"),
                                               parent=self.parent,
                                               modal=True,
                                               destroy_with_parent=True,
                                               message_type=Gtk.MessageType.QUESTION,
                                               buttons=Gtk.ButtonsType.OK_CANCEL,
                                               text=_("Are you sure you want to delete the invoice?"))
            confirm_dialog.connect("response", self.do_remove_invoice, invoice)
            confirm_dialog.show_all()
        else:
            self.do_remove_invoice(None, Gtk.ResponseType.OK, invoice)

    @Gtk.Template.Callback()
    def add_record(self, *args):
        dialog = RecordDialog(self.record_event)
        dialog.set_transient_for(self.parent)
        dialog.show_all()

    def do_add_record(self, event, record: Record):
        self.invoice_row_store.append(record.as_list())
        self.reload_cumulatives()
        self.invalidate()

    def reload_cumulatives(self):
        discount = 0.0
        subtotal = 0.0
        vat = 0.0
        total = 0.0
        for row in self.invoice_row_store:
            record = row[8]
            discount = round(discount + record.discount, 2)
            subtotal = round(subtotal + record.subtotal, 2)
            vat = round(vat + record.vat, 2)
            total = round(total + record.total, 2)
        self.grand_totals = [discount, subtotal, vat, total]
        the_format = "\\financial{%.2f}"
        self.vars[_('grandtotal')] = the_format % total
        self.vars[_('subtotal')] = the_format % subtotal
        self.vars[_('total_vat')] = the_format % vat
        self.vars[_('total_discount')] = the_format % discount

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
        window = PreferencesWindow(self.event, section='document_settings')
        window.set_transient_for(self.parent)
        window.show_all()

    @Gtk.Template.Callback()
    def open_info_preferences(self, btn):
        window = PreferencesWindow(self.event, section='info')
        window.set_transient_for(self.parent)
        window.show_all()

    @Gtk.Template.Callback()
    def open_table_preferences(self, btn):
        window = PreferencesWindow(self.event, section='table_config')
        window.set_transient_for(self.parent)
        window.show_all()

    def set_invoice_ending(self, preference, invoice_ending):
        self.invoice_ending.set_text(invoice_ending.format_map(self.vars))

    @Gtk.Template.Callback()
    def toggle_preview(self, btn):
        if btn.get_active():
            self.pdf.totals = self.grand_totals
            self.pdf.reload(self.vars)
            self.tex_project.run_tex()
            self.tex_project.run_previewer()
            self.tex_project.run_tex(run_once=False)
        else:
            self.tex_project.stop_tex()
            self.tex_project.stop_previewer()

    def invalidate(self, *args):
        self.address_store.clear()
        for address_line in self.customer.addresslines.split(os.linesep):
            self.address_store.append((address_line,))
        self.customer_info_store.load()
        self.supplier_info_store.load()
        self.table_column_store.load()
        self.cumulative_column_store.load()
        for col_idx, column in enumerate(self.table_column_store):
            col = self.invoice_records.get_column(col_idx)
            col.set_title(column.title)
            if col_idx > 1:
                col.set_alignment(1.0)
            if column.size_type == 0:
                col.set_visible(False)
            elif column.size_type == 1:
                col.set_sizing(1)
            elif column.size_type == 2:
                col.set_sizing(0)
        self.cumulative_records.get_model().clear()
        for col_idx, column in enumerate(self.cumulative_column_store):
            if column.size_type:
                self.cumulative_records.get_model().append(('<b>%s</b>' % column.title,
                                                            str(self.grand_totals[col_idx]),
                                                            1))
        self.set_invoice_ending(None, preference_store['invoice_ending'].value)
        if self.preview_toggle.get_active():
            self.pdf.totals = self.grand_totals
            self.pdf.reload(self.vars)
