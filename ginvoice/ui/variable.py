# GinVoice - Creating LaTeX invoices with a GTK GUI
# Copyright (C) 2021  Erik Nijenhuis <erik@xerdi.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi

from ginvoice.util import find_ui_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


@Gtk.Template.from_file(find_ui_file("variable.glade"))
class VariableEntry(Gtk.Entry):
    __gtype_name__ = "variable_entry"

    store = Gtk.Template.Child('variable_store')
    completion = Gtk.Template.Child('variable_completion')

    def __init__(self):
        Gtk.Entry.__init__(self)
        self.completion.set_match_func(self.complete_entry)

    @staticmethod
    def complete_entry(completion: Gtk.EntryCompletion, text: str, iter: Gtk.TreeIter):
        cursor = completion.get_entry().get_position()
        variable = completion.get_model().get_value(iter, 0)

        if cursor:
            begin = text.rfind('{', 0, cursor)
            end = max(min(text.find('}', cursor), text.find(' ', cursor)), cursor) \
                if len(text) > cursor \
                else max(text.find(' ', cursor), cursor)
            if begin < 0:
                return False
            return text[begin + 1:end] in variable
        else:
            return False

    @Gtk.Template.Callback()
    def complete_match_selected(self, completion: Gtk.EntryCompletion, model: Gtk.ListStore, iter: Gtk.TreeIter):
        entry = completion.get_entry()
        cursor = entry.get_position()
        text = entry.get_text()
        match = model.get_value(iter, 0)
        begin = text.rfind('{', 0, cursor)
        end = min(
            max(text.find('}', cursor), cursor),
            max(text.find(' ', cursor), cursor)
        )
        end_valid = end < len(text)
        ending = text[end:] if end_valid else ''
        if not end_valid or (end_valid and text[end] != '}'):
            match += '}'
        result = text[:begin + 1] + match + ending
        entry.set_text(result)
        entry.set_position(begin + len(match) + 1)
        return True

