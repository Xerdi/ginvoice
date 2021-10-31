import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ginvoice.common import signal


@signal()
def search_toggle(btn, revealer):
    if isinstance(revealer, Gtk.Revealer):
        revealer.set_reveal_child(not revealer.get_reveal_child())
    else:
        revealer.set_search_mode(not revealer.get_search_mode())


@signal()
def on_search_change(entry, listbox):
    listbox.invalidate_filter()
