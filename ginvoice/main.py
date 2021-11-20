import sys, gi
from ginvoice.ui.app import GinVoiceWindow

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.xerdi.ginvoice",
                         flags=Gio.ApplicationFlags.FLAGS_NONE, **kwargs)
        self.window = None

    def do_activate(self):
        self.window = self.window or GinVoiceWindow(application=self)
        self.window.present()


def main():
    Application().run(sys.argv)


if __name__ == '__main__':
    main()
