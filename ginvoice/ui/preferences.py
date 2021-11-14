import gi

from ginvoice.util import find_ui_file, find_css_file
from ginvoice.model.preference import preference_store

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


def parse_bool(v):
    if isinstance(v, str):
        return v == 'True'
    return v


@Gtk.Template.from_file(find_ui_file("preferences.glade"))
class PreferencesWindow(Gtk.Window):

    __gtype_name__ = "preferences_window"

    invoice_counter = Gtk.Template.Child('invoice_counter')
    customer_counter = Gtk.Template.Child('customer_counter')

    profile_removal = Gtk.Template.Child('removal_profile')
    customer_removal = Gtk.Template.Child('customer_removal')
    invoice_removal = Gtk.Template.Child('invoice_removal')
    record_removal = Gtk.Template.Child('record_removal')

    locale = Gtk.Template.Child('locale')
    babel = Gtk.Template.Child('babel')
    currency = Gtk.Template.Child('currency')

    def __init__(self):
        Gtk.Window.__init__(self)
        self.invoice_counter.set_text(str(preference_store['invoice_counter'].value))
        self.customer_counter.set_text(str(preference_store['customer_counter'].value))

        self.profile_removal.set_active(parse_bool(preference_store['show_profile_removal'].value))
        self.customer_removal.set_active(parse_bool(preference_store['show_customer_removal'].value))
        self.invoice_removal.set_active(parse_bool(preference_store['show_invoice_removal'].value))
        self.record_removal.set_active(parse_bool(preference_store['show_record_removal'].value))

        self.locale.get_model()[0][1] = ''
        self.locale.set_active_id(preference_store['locale'].value)
        self.currency.set_active_id(preference_store['currency'].value)
        self.babel.set_active_id(preference_store['babel'].value)

    @Gtk.Template.Callback()
    def validate_number(self, widget):
        raw = widget.get_text()
        val = ''.join([c for c in raw if c.isdigit()])
        widget.set_text(val)
        return raw == val

    @Gtk.Template.Callback()
    def change_invoice_counter(self, widget):
        preference_store['invoice_counter'] = int(widget.get_text())

    @Gtk.Template.Callback()
    def change_customer_counter(self, widget):
        preference_store['customer_counter'] = int(widget.get_text())

    @Gtk.Template.Callback()
    def change_locale(self, combobox):
        preference_store['locale'] = combobox.get_active_id()

    @Gtk.Template.Callback()
    def change_babel(self, combobox):
        preference_store['babel'] = combobox.get_active_id()

    @Gtk.Template.Callback()
    def change_currency(self, combobox):
        preference_store['currency'] = combobox.get_active_id()

    @Gtk.Template.Callback()
    def save_changes(self, btn):
        preference_store.commit()
        self.destroy()

    @Gtk.Template.Callback()
    def cancel_changes(self, btn):
        preference_store.load()
        self.destroy()

    @Gtk.Template.Callback()
    def change_confirmation(self, switch, state):
        preference_store[switch.get_name()] = state


if __name__ == '__main__':
    import ginvoice.i18n
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    provider.load_from_path(find_css_file('style.css'))

    window = PreferencesWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
