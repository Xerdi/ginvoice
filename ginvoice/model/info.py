import os, json, gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk


class GenericInfoStore(Gtk.ListStore):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    data_file = GObject.Property(type=str)

    def __init__(self, data_file) -> None:
        Gtk.ListStore.__init__(self, str, str)
        self.data_file = data_file

    def load(self):
        self.clear()
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for raw in data:
                    self.append((raw['key'], raw['value']))

    def commit(self):
        with open(self.data_file, 'w') as f:
            json.dump([{'key': c[0], 'value': c[1]} for c in self], f)


