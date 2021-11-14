import sys, gi
from ginvoice.ui.app import GinVoiceWindow
from ginvoice.util import find_css_file

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk, Gdk


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.xerdi.ginvoice",
                         flags=Gio.ApplicationFlags.FLAGS_NONE, **kwargs)
        self.window = None

    def do_activate(self):
        self.window = self.window or GinVoiceWindow(application=self)
        self.window.present()


if __name__ == '__main__':
    import ginvoice.i18n
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    provider.load_from_path(find_css_file('style.css'))
    Application().run(sys.argv)
