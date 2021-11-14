import gi

from ginvoice.util import find_ui_file, find_css_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


@Gtk.Template.from_file(find_ui_file("profile.glade"))
class ProfileWindow(Gtk.Window):

    __gtype_name__ = "profile_window"

    # customer_listbox = Gtk.Template.Child('customer_listbox')
    # search = Gtk.Template.Child('customer_search_entry')

    def __init__(self):
        Gtk.Window.__init__(self)


if __name__ == '__main__':
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    provider.load_from_path(find_css_file('style.css'))

    window = ProfileWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
