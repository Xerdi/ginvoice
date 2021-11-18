import os

import gi

from ginvoice.model.preference import preference_store
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


@Gtk.Template.from_file(find_ui_file("customer.glade"))
class CustomerWindow(Gtk.Window):

    __gtype_name__ = "customer_dialog"

    number = Gtk.Template.Child('number')
    name = Gtk.Template.Child('name')
    salutation = Gtk.Template.Child('salutation')
    street = Gtk.Template.Child('street')
    postal = Gtk.Template.Child('postal')

    existing = True

    def __init__(self, customer):
        Gtk.Window.__init__(self)
        self.customer = customer
        if self.customer.id:
            self.salutation.grab_focus()
            self.name.set_sensitive(False)
            self.number.set_text(str(self.customer.id))
            self.name.set_text(self.customer.name)
            a1, a2, a3 = self.customer.addresslines.split(os.linesep)
            self.salutation.set_text(a1)
            self.street.set_text(a2)
            self.postal.set_text(a3)
        else:
            self.number.set_text(str(preference_store['customer_counter'].value))
            self.name.grab_focus()
            self.existing = False

    @Gtk.Template.Callback()
    def cancel(self, btn):
        self.destroy()

    @Gtk.Template.Callback()
    def save(self, btn):
        if not self.existing:
            preference_store['customer_counter'] = int(preference_store['customer_counter'].value) + 1
            preference_store.commit()
        self.customer.id = int(self.number.get_text())
        self.customer.name = self.name.get_text()
        self.customer.addresslines = os.linesep.join([
            self.salutation.get_text(), self.street.get_text(), self.postal.get_text()
        ])
        self.customer.emit('changed' if self.existing else 'created')
        self.destroy()

    @Gtk.Template.Callback()
    def name_changed(self, entry):
        self.salutation.set_text(entry.get_text())
