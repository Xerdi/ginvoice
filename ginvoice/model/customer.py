import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject


class Customer(GObject.GObject):

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    id = GObject.Property(type=int)
    name = GObject.Property(type=str)
    addresslines = GObject.Property(type=str)

    def __init__(self):
        GObject.GObject.__init__(self)

    def set_address(self, lines):
        self.addresslines = lines
        self.emit('changed', self)

