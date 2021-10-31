import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.overrides.Gio import Gio

from ginvoice.environment import get_resource
from ginvoice.ui import *
from ginvoice.common import connect_signal


class GinVoiceApplication:
    builder = Gtk.Builder()
    profiles_store = Gio.ListStore()

    def __init__(self, glade_file, css=None):
        self.builder.add_from_file(glade_file)
        self.builder.connect_signals_full(connect_signal, self)
        # self.builder.connect_signals(__SIGNAL_HANDLERS__)
        self.window = self.builder.get_object('window')
        profiles_list_box = self.builder.get_object('profiles_list_box')
        profiles_list_box.bind_model(self.profiles_store, self.create_profile_row)
        self.customers = self.builder.get_object('customer_list_box')
        self.search = self.builder.get_object('customer_search_entry')
        self.customers.set_filter_func(self.filter_customers, self.search)
        if css:
            screen = Gdk.Screen.get_default()
            provider = Gtk.CssProvider()
            style_context = Gtk.StyleContext()
            style_context.add_provider_for_screen(
                screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            provider.load_from_path(css)

    @staticmethod
    def search_toggle(reveal):
        if isinstance(reveal, Gtk.Revealer):
            reveal.set_reveal_child(not reveal.get_reveal_child())
        else:
            reveal.set_search_mode(not reveal.get_search_mode())

    @staticmethod
    def on_search_change(listbox):
        listbox.invalidate_filter()

    @staticmethod
    def filter_customers(row, search):
        return search.get_text().lower() in row.get_child().get_text().lower()

    @staticmethod
    def open_profiles(dialog):
        dialog.show_all()

    def create_profile_row(self, ud):
        print(ud)

    def set_default_profile(self, *args):
        print(*args)


def find_resources():
    cmd = sys.argv[0]
    if cmd.endswith('.py'):
        return "../res/glade/app.glade", "../res/style.css"
    return get_resource("app.glade"), get_resource("style.css")


def filter_fn(row, ud):
    print(row, ud)
    return True


if __name__ == '__main__':
    glade_file, css_file = find_resources()
    app = GinVoiceApplication(glade_file, css=css_file)
    for i in range(15):
        r = Gtk.ListBoxRow()
        r.add(Gtk.Label(label='hoi'))
        r.show_all()
        app.customers.add(r)
    app.window.connect("destroy", Gtk.main_quit)
    app.window.show_all()
    Gtk.main()
