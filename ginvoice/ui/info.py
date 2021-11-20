import gi

from ginvoice.model.info import GenericInfoStore
from ginvoice.ui import variable
from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@Gtk.Template.from_file(find_ui_file("info.glade"))
class InfoWindow(Gtk.Window):
    __gtype_name__ = "info_dialog"

    title = Gtk.Template.Child('title')
    value = Gtk.Template.Child('value')
    repeat = Gtk.Template.Child('repeat_checkbox')

    def __init__(self, title: str, store: GenericInfoStore):
        Gtk.Window.__init__(self)
        self.set_title(title)
        self.store = store

    @Gtk.Template.Callback()
    def save(self, btn):
        self.store.append((self.title.get_text(), self.value.get_text()))
        if self.repeat.get_active():
            self.title.set_text('')
            self.value.set_text('')
            self.title.grab_focus()
        else:
            self.destroy()

    @Gtk.Template.Callback()
    def close(self, btn):
        self.destroy()
