
import gi

from ginvoice.model.preference import preference_store
from ginvoice.util import find_css_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class Style:
    screen = Gdk.Screen.get_default()
    style_context = Gtk.StyleContext()

    def __init__(self):
        provider = Gtk.CssProvider()
        self.style_context.add_provider_for_screen(
            self.screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        provider.load_from_path(find_css_file('style.css'))
        preference_store['foreground_color'].connect('changed', self.load_css)
        preference_store['background_color'].connect('changed', self.load_css)
        self.load_css()

    def load_css(self, *args):
        provider = Gtk.CssProvider()
        self.style_context.add_provider_for_screen(
            self.screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        provider.load_from_data(
            bytes((".headerfg { color: %s; } .headerbg { background-color: %s; }" %
                   (preference_store['foreground_color'].value, preference_store['background_color'].value)).encode()))
