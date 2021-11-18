import getpass
import json

import gi

from ginvoice.model.customer import Customer

gi.require_version("Gtk", "3.0")
from gi.repository import GObject


class Invoice(GObject.GObject):
    idx = GObject.Property(type=int)
    customer = GObject.Property(type=Customer)
    ending = GObject.Property(type=str)
