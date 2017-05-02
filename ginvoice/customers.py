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
import os
from gi.repository import Gtk

from ginvoice.form import Form
from ginvoice.environment import data_dir, customer_file
from ginvoice.widgets.table import Table
from ginvoice.i18n import _

handling_selection = False


class CustomerController:

    def __init__(self, sidebar):
        self.sidebar = sidebar
        self.tables = {}

        self._load_customers()

    def get_customer_details(self):
        return self.customers[self.sidebar.stack.get_visible_child_name()]

    def get_current_record_store(self):
        selected = self.sidebar.stack.get_visible_child_name()
        if selected:
            return self.tables[selected].record_store

    def on_create(self, button):
        dialog = Gtk.Dialog()
        dialog.set_title(_("Add Customer"))

        def create_action(record):
            self._store_customer(record)
            dialog.destroy()

        form = self._get_form(create_action)
        dialog.get_content_area().pack_end(form, True, True, 0)
        dialog.show_all()

    def on_destroy(self, button):
        name = self.sidebar.stack.get_visible_child_name()
        child = self.sidebar.stack.get_visible_child()
        if name:
            self.sidebar.stack.remove(child)
            self._remove_customer(name)

    def on_edit(self, button):
        dialog = Gtk.Dialog()
        dialog.set_title(_("Edit Customer"))

        def edit_action(record):
            self._edit_customer(record)
            dialog.destroy()

        form = self._get_form(edit_action)
        if os.path.exists(customer_file):
            name = self.sidebar.stack.get_visible_child_name()
            with open(customer_file, 'r') as f:
                data = json.load(f)
                form.load(data[name])

        dialog.get_content_area().pack_end(form, True, True, 0)
        dialog.show_all()

    def _get_form(self, action):
        form = Form(action=action)
        form.add_text_field("name", _("Name"))
        form.add_text_field("street", _("Address"))
        form.add_text_field("postal", _("Postal Code"))
        return form

    def _load_customers(self):
        file = customer_file
        if os.path.exists(file):
            with open(file, 'r') as f:
                self.customers = json.load(f)

                for customer in self.customers.keys():
                    self.sidebar.add_titled(self.create_records_view(customer), customer, customer)
        else:
            self.customers = {}

    def _store_customer(self, record):
        name = record["name"]
        self.customers[name] = record
        self.sidebar.stack.add_titled(self.create_records_view(name), name, name)
        with open(customer_file, 'w') as f:
            json.dump(self.customers, f)

    def _edit_customer(self, record):
        name = record["name"]
        self.customers[name] = record
        with open(customer_file, 'w') as f:
            json.dump(self.customers, f)

    def _remove_customer(self, name):
        del self.customers[name]
        with open(customer_file, 'w') as f:
            json.dump(self.customers, f)

    def create_records_view(self, customer):
        records_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        form_wrapper = Gtk.Revealer()

        form = Form(with_buttons=False)
        form_wrapper.add(form)
        client_entry = form.add_text_field("client", _("Client"))
        date_entry = form.add_text_field("date", _("Date"))
        desc_entry = form.add_text_field("description", _("Description"))
        fixed_entry = form.add_switch("type", _("Fixed Price"))
        amount_entry = form.add_number_field("value", _("Value"))

        table = Table()

        self.tables[customer] = table

        def gen_input_change(selection, row_idx):

            def change(entry):
                if handling_selection:
                    return
                model, tree_iterator = selection.get_selected()
                if model and tree_iterator:
                    model[tree_iterator][row_idx] = entry.get_text()

            return change

        def gen_switch_change(selection):
            def switch_input_change(entry, active):
                if handling_selection:
                    return
                model, tree_iterator = selection.get_selected()
                if model and tree_iterator:
                    model[tree_iterator][0] = _("Fixed Price") if active else _("Minutes")
            return switch_input_change

        def selection_change(selection):
            store, tree_iterator = selection.get_selected()
            form_wrapper.set_reveal_child(tree_iterator is not None)
            if store and tree_iterator:
                global handling_selection
                handling_selection = True
                model = store[tree_iterator]
                fixed_entry.set_active(model[0] == _('Fixed Price'))
                client_entry.set_text(model[1])
                date_entry.set_text(model[2])
                desc_entry.set_text(model[3])
                amount_entry.set_text(model[4])
                handling_selection = False

        _selection = table.table.get_selection()
        _selection.connect("changed", selection_change)
        fixed_entry.connect("state-set", gen_switch_change(_selection))
        client_entry.connect("changed", gen_input_change(_selection, 1))
        date_entry.connect("changed", gen_input_change(_selection, 2))
        desc_entry.connect("changed", gen_input_change(_selection, 3))
        amount_entry.connect("changed", gen_input_change(_selection, 4))

        def create_or_select_record(button):
            found = None
            for record in table.record_store:
                match = True
                for i in range(0, 4):
                    if record[i] != '':
                        match = False
                        break
                if match:
                    found = record
                    break

            if found:
                table.table.get_selection().select_iter(found.iter)
            else:
                table.new_record()

        def remove_selected(button):
            model, iter = table.table.get_selection().get_selected()
            if iter:
                table.record_store.remove(iter)

        action_bar = Gtk.ActionBar()

        add_button = Gtk.ToolButton()
        add_button.set_tooltip_text(_("Create Record"))
        add_button.set_icon_name("list-add")
        add_button.connect("clicked", create_or_select_record)
        action_bar.add(add_button)

        remove_button = Gtk.ToolButton()
        remove_button.set_tooltip_text(_("Remove Record"))
        remove_button.set_icon_name("list-remove")
        remove_button.connect("clicked", remove_selected)
        action_bar.add(remove_button)

        records_view.pack_start(table, False, False, 0)
        records_view.set_child_packing(table, True, True, 0, Gtk.PackType.START)
        records_view.add(action_bar)
        records_view.add(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        records_view.pack_end(form_wrapper, False, False, 0)
        records_view.set_child_packing(form, False, False, 0, Gtk.PackType.END)
        records_view.show_all()
        table.new_record()
        return records_view
