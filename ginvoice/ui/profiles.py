import gi

from ginvoice.ui.profile import ProfileWindow
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@Gtk.Template.from_file(find_ui_file("profiles.glade"))
class ProfilesWindow(Gtk.Window):

    __gtype_name__ = "profiles_dialog"

    # customer_listbox = Gtk.Template.Child('customer_listbox')
    # search = Gtk.Template.Child('customer_search_entry')

    def __init__(self):
        Gtk.Window.__init__(self)

    @Gtk.Template.Callback()
    def create_profile(self, *args):
        dialog = ProfileWindow()
        dialog.set_transient_for(self)
        dialog.show_all()


if __name__ == '__main__':
    window = ProfilesWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
