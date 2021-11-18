import os, gi

from ginvoice.model.customer import Customer
from ginvoice.model.preference import preference_store
from ginvoice.model.style import Style
from ginvoice.util import find_ui_file, find_css_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject


screen = Gdk.Screen.get_default()
provider = Gtk.CssProvider()
style_context = Gtk.StyleContext()
style_context.add_provider_for_screen(
    screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)
provider.load_from_path(find_css_file('style.css'))


@Gtk.Template.from_file(find_ui_file("invoice.glade"))
class InvoiceForm(Gtk.Box):
    __gtype_name__ = "invoice"

    title = Gtk.Template.Child('title')
    subtitle = Gtk.Template.Child('subtitle')

    addressline1 = Gtk.Template.Child('addressline1')
    addressline2 = Gtk.Template.Child('addressline2')
    addressline3 = Gtk.Template.Child('addressline3')

    def __init__(self, invoice_stack: Gtk.Stack, customer: Customer, idx: int):
        super().__init__()
        self.invoice_stack = invoice_stack
        self.idx = idx
        self.customer = customer
        self.customer.connect('changed', self.update_address)
        self.update_address(customer)
        self.title.set_text(preference_store['title'].value)
        preference_store['title'].connect('changed', self.set_title)
        self.subtitle.set_text(preference_store['subtitle'].value)
        preference_store['subtitle'].connect('changed', self.set_subtitle)

    def update_address(self, customer: Customer):
        a1, a2, a3 = customer.addresslines.split(os.linesep)
        self.addressline1.set_text(a1)
        self.addressline2.set_text(a2)
        self.addressline3.set_text(a3)

    def set_title(self, preference, title):
        self.title.set_text(title)

    def set_subtitle(self, preference, subtitle):
        self.subtitle.set_text(subtitle)

    @Gtk.Template.Callback()
    def remove_invoice(self, invoice):
        self.invoice_stack.remove(invoice)

    def set_idx(self, idx: int):
        self.idx = idx

    def set_customer(self, customer: Customer):
        self.customer.disconnect_by_func(self.update_address)
        self.customer = customer
        self.customer.connect('changed', self.update_address)
        self.update_address(self.customer)


if __name__ == '__main__':
    Style()
    window = Gtk.Window()
    window.add(InvoiceForm())
    window.connect('destroy', Gtk.main_quit)
    window.show_all()
    Gtk.main()
