import os
import shutil

import gi

from ginvoice.environment import image_dir
from ginvoice.util import find_ui_file, find_css_file
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

    def __init__(self):
        Gtk.Window.__init__(self)
        self.title.set_text(preference_store['title'].value)
        self.subtitle.set_text(preference_store['subtitle'].value)
        self.author.set_text(preference_store['author'].value)
        self.keywords.set_text(preference_store['keywords'].value)

        def filter_mono(family, face, include):
            return family.is_monospace() == include

        self.main_font.set_filter_func(filter_mono, False)
        self.main_font.set_font_name(preference_store['main_font'].value)
        self.mono_font.set_filter_func(filter_mono, True)
        self.mono_font.set_font_name(preference_store['mono_font'].value)
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
        preference_store['invoice_counter'] = int(widget.get_text())

    @Gtk.Template.Callback()
    def change_customer_counter(self, widget):
        preference_store['customer_counter'] = int(widget.get_text())

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
        self.destroy()

    @Gtk.Template.Callback()
    def cancel_changes(self, btn):
        preference_store.load()
        self.destroy()

    @Gtk.Template.Callback()
    def change_confirmation(self, switch, state):
        preference_store[switch.get_name()] = state


if __name__ == '__main__':
    import ginvoice.i18n
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(
        screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    provider.load_from_path(find_css_file('style.css'))

    window = PreferencesWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
