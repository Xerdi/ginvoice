import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ginvoice.common import signal


@signal()
def open_profiles(btn, dialog):
    dialog.show_all()


@signal()
def create_profile(*args):
    print(*args)


@signal()
def set_default_profile(*args):
    print(*args)
