import getpass
import json

import gi

from ginvoice.environment import preferences_file

gi.require_version("Gtk", "3.0")
from gi.repository import GObject


class Preference(GObject.GObject):

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    name = GObject.Property(type=str)
    value = GObject.Property()
    default = GObject.Property()

    def __init__(self, name, default=None):
        GObject.GObject.__init__(self)
        self.name = name
        self.value = default
        self.default = default

    def set_value(self, value):
        self.value = value
        self.emit('changed', value)


class PreferenceStore(GObject.GObject):

    preferences = dict()
    data_file = GObject.Property(type=str, default=preferences_file)
    data_cache = {}

    def __init__(self):
        GObject.GObject.__init__(self)

    def add_preference(self, preference: Preference):
        preference.value = self.data_cache[preference.name]\
            if preference.name in self.data_cache else preference.default
        preference.connect('changed', self.update_preference)
        self.preferences[preference.name] = preference

    def update_preference(self, preference: Preference, value):
        self.data_cache[preference.name] = value

    def load(self):
        with open(self.data_file, 'r') as f:
            self.data_cache = json.load(f)
        for k, v in self.data_cache.items():
            if k not in self.preferences:
                print("Key %s missing" % k)
                continue
            self.preferences[k].value = v

    def commit(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data_cache, f)

    def __setitem__(self, name, value):
        self.preferences[name].set_value(value)

    def __getitem__(self, name) -> Preference:
        return self.preferences[name]

    def __iter__(self):
        return self.preferences.values()

    def __contains__(self, name):
        return name in self.preferences

    def __iadd__(self, other):
        self.add_preference(other)
        return self


preference_store = PreferenceStore()

# Document
preference_store += Preference('title', default='')
preference_store += Preference('subtitle', default='')
preference_store += Preference('author', default=getpass.getuser())
preference_store += Preference('keywords', default='')

# Document styling
preference_store += Preference('main_font', default='Sans')
preference_store += Preference('mono_font', default='Monospace')
preference_store += Preference('foreground_color', default='#000000')
preference_store += Preference('background_color', default='#ffffff')

# Footer images
preference_store += Preference('footer_image_1')
preference_store += Preference('footer_image_2')
preference_store += Preference('footer_image_3')

# Counters
preference_store += Preference('invoice_counter', default='1')
preference_store += Preference('customer_counter', default='1')

# Language and currency
preference_store += Preference('locale', default='')
preference_store += Preference('babel', default='english')
preference_store += Preference('currency', default='€')
preference_store += Preference('active_profile', default='Default')

# Dialog confirmations
preference_store += Preference('show_profile_removal', default=True)
preference_store += Preference('show_customer_removal', default=True)
preference_store += Preference('show_invoice_removal', default=True)
preference_store += Preference('show_record_removal', default=True)
preference_store.load()
