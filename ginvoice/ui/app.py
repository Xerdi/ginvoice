
import gi

from ginvoice.model.customer import Customer, CustomerStore
from ginvoice.model.preference import preference_store
from ginvoice.model.style import Style
from ginvoice.ui.customer import CustomerWindow
from ginvoice.ui.invoice import InvoiceForm
from ginvoice.ui.preferences import PreferencesWindow
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ginvoice.i18n import _


@Gtk.Template.from_file(find_ui_file("app.glade"))
class GinVoiceWindow(Gtk.ApplicationWindow):

    __gtype_name__ = "app_window"

    customer_store = CustomerStore()
    customer_listbox = Gtk.Template.Child('sidebar_listbox')
    search = Gtk.Template.Child('sidebar_search_entry')
    search_toggle = Gtk.Template.Child('sidebar_search_toggle')
    search_revealer = Gtk.Template.Child('sidebar_search_revealer')
    remove_btn = Gtk.Template.Child('remove_customer')
    edit_btn = Gtk.Template.Child('edit_customer')
    add_invoice_btn = Gtk.Template.Child('add_invoice')
    invoice_stack = Gtk.Template.Child('invoice_stack')
    invoice_switcher = Gtk.Template.Child('invoice_switcher')
    switcher_revealer = Gtk.Template.Child('switcher_revealer')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = Style()
        self.customer_listbox.bind_model(self.customer_store, self.create_customer_row)
        self.customer_listbox.set_filter_func(self.filter_customers)
        self.customer_store.load()
        preference_store['invoice_counter'].connect('changed', self.recalculate_indexes)

    def filter_customers(self, row):
        return self.search.get_text().lower() in self.customer_store[row.get_index()].name.lower()

    @Gtk.Template.Callback()
    def open_preferences(self, *args):
        window = PreferencesWindow()
        window.set_transient_for(self)
        window.show_all()

    def customer_created(self, customer: Customer):
        self.customer_store.append(customer)
        self.customer_store.commit()

    @Gtk.Template.Callback()
    def add_customer(self, btn):
        customer = Customer()
        customer.connect('created', self.customer_created)
        window = CustomerWindow(customer)
        window.set_transient_for(self)
        window.show_all()

    def customer_changed(self, customer: Customer):
        self.customer_store.commit()

    @Gtk.Template.Callback()
    def edit_customer(self, listbox):
        customer = self.customer_store[listbox.get_selected_row().get_index()]
        customer.connect('changed', self.customer_changed)
        window = CustomerWindow(customer)
        window.set_transient_for(self)
        window.show_all()

    def do_remove_customer(self, dialog, response, listbox):
        if response == Gtk.ResponseType.OK:
            self.customer_store.remove(listbox.get_selected_row().get_index())
            self.customer_store.commit()
        else:
            self.customer_store.load()
        dialog.destroy()

    @Gtk.Template.Callback()
    def remove_customer(self, listbox):
        confirm_dialog = Gtk.MessageDialog(title=_("Delete Customer Confirmation"),
                                           parent=self,
                                           modal=True,
                                           destroy_with_parent=True,
                                           message_type=Gtk.MessageType.QUESTION,
                                           buttons=Gtk.ButtonsType.OK_CANCEL,
                                           text=_("Are you sure you want to delete the customer?"))
        confirm_dialog.connect("response", self.do_remove_customer, listbox)
        confirm_dialog.show_all()

    @Gtk.Template.Callback()
    def search_changed(self, listbox):
        listbox.invalidate_filter()

    @Gtk.Template.Callback()
    def toggle_sidebar_search(self, btn):
        self.search_revealer.set_reveal_child(btn.get_active())
        if btn.get_active():
            self.search.grab_focus()

    @Gtk.Template.Callback()
    def focus_sidebar_search(self, entry, focus_event):
        self.search_revealer.set_reveal_child(False)
        self.search_toggle.set_active(False)

    @Gtk.Template.Callback()
    def customer_selected(self, listbox, row):
        self.edit_btn.set_sensitive(row is not None)
        self.remove_btn.set_sensitive(row is not None)
        self.add_invoice_btn.set_sensitive(row is not None)
        invoice_view = self.invoice_stack.get_visible_child()
        if invoice_view:
            invoice_view.set_customer(self.customer_store[row.get_index()])

    def invoice_title(self, idx):
        return _('Invoice') + ' ' + str(int(preference_store['invoice_counter'].value) + idx)

    @Gtk.Template.Callback()
    def add_invoice(self, btn):
        customer = self.customer_store[self.customer_listbox.get_selected_row().get_index()]
        invoice = InvoiceForm(self, self.invoice_stack, customer, len(self.invoice_stack))
        title = self.invoice_title(len(self.invoice_stack))
        self.invoice_stack.add_titled(invoice, title, title)

    @Gtk.Template.Callback()
    def show_switcher(self, stack, invoice):
        self.switcher_revealer.set_reveal_child(len(self.invoice_stack))

    def recalculate_indexes(self, preference, idx):
        if idx:
            self.handle_idx_gap(self.invoice_stack, None)

    @Gtk.Template.Callback()
    def handle_idx_gap(self, stack, removed_invoice):
        for idx, invoice in enumerate(stack):
            invoice.set_idx(idx)
            self.invoice_stack.child_set_property(invoice, 'title', self.invoice_title(idx))

    @staticmethod
    def create_customer_row(customer):
        row = Gtk.ListBoxRow()
        wrapper = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        idx = Gtk.Label(label=str(customer.id))
        idx.set_visible(False)
        idx.set_child_visible(False)
        wrapper.add(idx)
        wrapper.add(Gtk.Label(label=customer.name))
        row.add(wrapper)
        row.show_all()
        return row
