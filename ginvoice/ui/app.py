
import gi

from ginvoice.model.customer import Customer
from ginvoice.ui.customer import CustomerWindow
from ginvoice.ui.preferences import PreferencesWindow
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


@Gtk.Template.from_file(find_ui_file("app.glade"))
class GinVoiceWindow(Gtk.ApplicationWindow):

    __gtype_name__ = "app_window"

    customer_store = Gio.ListStore()
    customer_listbox = Gtk.Template.Child('sidebar_listbox')
    search = Gtk.Template.Child('sidebar_search_entry')
    search_toggle = Gtk.Template.Child('sidebar_search_toggle')
    search_revealer = Gtk.Template.Child('sidebar_search_revealer')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_listbox.bind_model(self.customer_store, self.create_customer_row)
        self.customer_listbox.set_filter_func(self.filter_customers)
        c1 = Customer()
        c1.id = 1
        c1.name = "John Doe"
        c1.addresslines = "Grapefruit Inc.\nasd 123\n1234as, asdjk"
        self.customer_store.append(c1)

    def filter_customers(self, row):
        return self.search.get_text().lower() in row.get_child().get_text().lower()

    @Gtk.Template.Callback()
    def open_preferences(self, *args):
        window = PreferencesWindow()
        window.set_transient_for(self)
        window.show_all()

    @Gtk.Template.Callback()
    def add_customer(self, btn):
        window = CustomerWindow()
        window.set_transient_for(self)
        window.show_all()

    @Gtk.Template.Callback()
    def toggle_sidebar_search(self, btn):
        self.search_revealer.set_reveal_child(btn.get_active())
        if btn.get_active():
            self.search.grab_focus()

    @Gtk.Template.Callback()
    def focus_sidebar_search(self, entry, focus_event):
        self.search_revealer.set_reveal_child(False)
        self.search_toggle.set_active(False)

    def create_customer_row(self, customer):
        row = Gtk.ListBoxRow()
        row.add(Gtk.Label(label=customer.name))
        row.show_all()
        return row
