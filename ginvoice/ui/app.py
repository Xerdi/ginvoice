
import gi

from ginvoice.ui.preferences import PreferencesWindow
from ginvoice.ui.profiles import ProfilesWindow
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@Gtk.Template.from_file(find_ui_file("app.glade"))
class GinVoiceWindow(Gtk.ApplicationWindow):

    __gtype_name__ = "app_window"

    customer_listbox = Gtk.Template.Child('customer_listbox')
    search = Gtk.Template.Child('customer_search_entry')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_listbox.set_filter_func(self.filter_customers)

    def filter_customers(self, row):
        return self.search.get_text().lower() in row.get_child().get_text().lower()

    @Gtk.Template.Callback()
    def open_profiles(self, *args):
        window = ProfilesWindow()
        window.set_transient_for(self)
        window.show_all()

    @Gtk.Template.Callback()
    def open_preferences(self, *args):
        window = PreferencesWindow()
        window.set_transient_for(self)
        window.show_all()
