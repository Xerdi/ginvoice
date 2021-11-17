
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

    def __init__(self, customer=None):
        Gtk.Window.__init__(self)
        self.customer = customer
        if not self.customer:
            self.number.set_text(str(preference_store['customer_counter'].value))

    @Gtk.Template.Callback()
    def cancel(self, btn):
        self.destroy()

    @Gtk.Template.Callback()
    def save(self, btn):
        preference_store['customer_counter'] += 1

    @Gtk.Template.Callback()
    def name_changed(self, entry):
        self.salutation.set_text(entry.get_text())
