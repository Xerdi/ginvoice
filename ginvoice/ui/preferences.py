import os
import re
import shutil

import gi

from ginvoice.environment import image_dir
from ginvoice.model.column import TableColumnStore, CumulativeColumnStore, Column, TableColumnHandler
from ginvoice.model.style import Style
from ginvoice.util import find_ui_file
from ginvoice.model.preference import preference_store

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


def parse_bool(v):
    if isinstance(v, str):
        return v == 'True'
    return v


@Gtk.Template.from_file(find_ui_file("preferences.glade"))
class PreferencesWindow(Gtk.Window):

    __gtype_name__ = "preferences_window"

    title = Gtk.Template.Child('title')
    subtitle = Gtk.Template.Child('subtitle')
    author = Gtk.Template.Child('author')
    keywords = Gtk.Template.Child('keywords')

    main_font = Gtk.Template.Child('main_font')
    mono_font = Gtk.Template.Child('mono_font')
    fg_color = Gtk.Template.Child('foreground_color')
    bg_color = Gtk.Template.Child('background_color')

    footer_image_1 = Gtk.Template.Child('footer_image_1')
    footer_image_2 = Gtk.Template.Child('footer_image_2')
    footer_image_3 = Gtk.Template.Child('footer_image_3')

    invoice_counter = Gtk.Template.Child('invoice_counter')
    customer_counter = Gtk.Template.Child('customer_counter')

    profile_removal = Gtk.Template.Child('removal_profile')
    customer_removal = Gtk.Template.Child('customer_removal')
    invoice_removal = Gtk.Template.Child('invoice_removal')
    record_removal = Gtk.Template.Child('record_removal')

    locale = Gtk.Template.Child('locale')
    babel = Gtk.Template.Child('babel')
    currency = Gtk.Template.Child('currency')

    settings_stack = Gtk.Template.Child('settings_stack')

    completion = Gtk.Template.Child('invoice_ending_completer')
    table_column_group = Gtk.Template.Child('table_column_group')

    table_columns = TableColumnStore()
    cumulative_columns = CumulativeColumnStore()

    def __init__(self, section=None):
        Gtk.Window.__init__(self)
        self.title.set_text(preference_store['title'].value)
        self.subtitle.set_text(preference_store['subtitle'].value)
        self.author.set_text(preference_store['author'].value)
        self.keywords.set_text(preference_store['keywords'].value)

        if section:
            self.settings_stack.set_visible_child_name(section)

        def filter_mono(family, face, include):
            return family.is_monospace() == include

        self.main_font.set_filter_func(filter_mono, False)
        self.main_font.set_font(preference_store['main_font'].value)
        self.mono_font.set_filter_func(filter_mono, True)
        self.mono_font.set_font(preference_store['mono_font'].value)
        fg_color = Gdk.RGBA()
        fg_color.parse(preference_store['foreground_color'].value)
        self.fg_color.set_rgba(fg_color)
        bg_color = Gdk.RGBA()
        bg_color.parse(preference_store['background_color'].value)
        self.bg_color.set_rgba(bg_color)

        self.footer_image_1.add_shortcut_folder(image_dir)
        self.footer_image_2.add_shortcut_folder(image_dir)
        self.footer_image_3.add_shortcut_folder(image_dir)
        if preference_store['footer_image_1'].value:
            self.footer_image_1.set_filename(os.path.join(image_dir, preference_store['footer_image_1'].value))
        if preference_store['footer_image_2'].value:
            self.footer_image_2.set_filename(os.path.join(image_dir, preference_store['footer_image_2'].value))
        if preference_store['footer_image_3'].value:
            self.footer_image_3.set_filename(os.path.join(image_dir, preference_store['footer_image_3'].value))

        self.invoice_counter.set_text(str(preference_store['invoice_counter'].value))
        self.customer_counter.set_text(str(preference_store['customer_counter'].value))

        self.profile_removal.set_active(parse_bool(preference_store['show_profile_removal'].value))
        self.customer_removal.set_active(parse_bool(preference_store['show_customer_removal'].value))
        self.invoice_removal.set_active(parse_bool(preference_store['show_invoice_removal'].value))
        self.record_removal.set_active(parse_bool(preference_store['show_record_removal'].value))

        self.locale.get_model()[0][1] = ''
        self.locale.set_active_id(preference_store['locale'].value)
        self.currency.set_active_id(preference_store['currency'].value)
        self.babel.set_active_id(preference_store['babel'].value)

        self.completion.set_match_func(self.complete_entry)
        table_column_rows = self.table_column_group.get_children()
        self.table_columns.load()
        # Setup default values from glade defaults
        if len(table_column_rows) != len(self.table_columns):
            for row in table_column_rows:
                c = Column()
                l, t, s, t = row.get_children()
                c.title = l.get_text()
                c.size_type = s.get_model()[s.get_active_iter()][0]
                c.text = t.get_text()
                self.table_columns.append(c)
        for idx, row in enumerate(table_column_rows):
            TableColumnHandler(*row.get_children()[1:], self.table_columns[idx])

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
        result = text[:begin+1] + match + ending
        entry.set_text(result)
        entry.set_position(begin + len(match) + 1)
        return True

    @Gtk.Template.Callback()
    def validate_number(self, widget):
        raw = widget.get_text()
        val = ''.join([c for c in raw if c.isdigit()])
        widget.set_text(val)
        return raw == val

    @Gtk.Template.Callback()
    def change_title(self, widget):
        preference_store['title'] = widget.get_text()

    @Gtk.Template.Callback()
    def change_subtitle(self, widget):
        preference_store['subtitle'] = widget.get_text()

    @Gtk.Template.Callback()
    def change_author(self, widget):
        preference_store['author'] = widget.get_text()

    @Gtk.Template.Callback()
    def change_keywords(self, widget):
        preference_store['keywords'] = widget.get_text()

    @Gtk.Template.Callback()
    def change_main_font(self, widget):
        preference_store['main_font'] = widget.get_font_family().get_name()

    @Gtk.Template.Callback()
    def change_mono_font(self, widget):
        preference_store['mono_font'] = widget.get_font_family().get_name()

    @staticmethod
    def _rgba_to_hex(rgba):
        return "#" + "".join(["%02x" % int(c * 255) for c in [rgba.red, rgba.green, rgba.blue]])

    @Gtk.Template.Callback()
    def change_fg_color(self, widget):
        preference_store['foreground_color'] = self._rgba_to_hex(widget.get_rgba())

    @Gtk.Template.Callback()
    def change_bg_color(self, widget):
        preference_store['background_color'] = self._rgba_to_hex(widget.get_rgba())

    @Gtk.Template.Callback()
    def change_footer_img1(self, widget):
        preference_store['footer_image_1'] = widget.get_filename()

    @Gtk.Template.Callback()
    def change_footer_img2(self, widget):
        preference_store['footer_image_2'] = widget.get_filename()

    @Gtk.Template.Callback()
    def change_footer_img3(self, widget):
        preference_store['footer_image_3'] = widget.get_filename()

    @Gtk.Template.Callback()
    def change_invoice_counter(self, widget):
        preference_store['invoice_counter'] = widget.get_text()

    @Gtk.Template.Callback()
    def change_customer_counter(self, widget):
        preference_store['customer_counter'] = widget.get_text()

    @Gtk.Template.Callback()
    def change_locale(self, combobox):
        preference_store['locale'] = combobox.get_active_id()

    @Gtk.Template.Callback()
    def change_babel(self, combobox):
        preference_store['babel'] = combobox.get_active_id()

    @Gtk.Template.Callback()
    def change_currency(self, combobox):
        preference_store['currency'] = combobox.get_active_id()

    @Gtk.Template.Callback()
    def save_changes(self, btn):
        for k in ['footer_image_1', 'footer_image_2', 'footer_image_3']:
            val = preference_store[k].value
            if val and not val.startswith(image_dir):
                shutil.copy(val, image_dir)
                preference_store[k] = os.path.basename(val)
        preference_store.commit()
        self.table_columns.commit()
        self.destroy()

    @Gtk.Template.Callback()
    def cancel_changes(self, btn):
        preference_store.load()
        self.table_columns.load()

        self.destroy()

    @Gtk.Template.Callback()
    def change_confirmation(self, switch, state):
        preference_store[switch.get_name()] = state


if __name__ == '__main__':
    import ginvoice.i18n
    Style()
    window = PreferencesWindow(section='table_config')
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
