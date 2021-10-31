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
import json
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.overrides.Gio import Gio
from gi.repository import GObject
from gi.repository import Gtk

from ginvoice.environment import get_profile, get_profiles
from ginvoice.preferences import set_preference, get_preference

from ginvoice.i18n import _
from ginvoice.form import Form, text_not_none


def filter_mono(family, face, include):
    return family.is_monospace() == include


def save_profile(data):
    file_target = get_profile(data['profile_name'])
    with open(file_target, 'w') as f:
        json.dump(data, f)
    return True


def increment_invoice():
    file_target = get_profile(get_preference('active_profile'))
    with open(file_target, 'r') as f:
        data = json.load(f)
        data["invoice_nr"] = str(int(data["invoice_nr"])+1)
    if data:
        with open(file_target, 'w') as f:
            json.dump(data, f)
    else:
        raise "Couldn't write invoice number"


def get_create_profile_form(action=save_profile, data=None):
    form = Form(action=action)
    form.add_text_field("profile_name", _("Profile Name"),
                        validator=text_not_none,
                        tooltip=_("Required"),
                        default_value=_('Default'))
    form.add_section(_("Basic Invoice Details"))
    form.add_text_field("author", _("Author"), validator=text_not_none, tooltip=_("Required"))
    form.add_text_field("title", _("Title"), validator=text_not_none)
    form.add_text_field("subtitle", _("Subtitle"))
    form.add_number_field("invoice_nr", _("Next Invoice Number"), default_value='1')

    # TODO implement Gtk.TextView
    form.add_text_field("ending", _("Ending"), default_value=_("Please send us the total of \\grandtotal{}\n\
within the coming 14 days\n\
to account number NL00 0000 0000 0000 0000 00\n\
with the note of the invoice number \\invoicenr{}.\n\
\n\
Questions about this invoice?\n\
Please contact us."))

    form.add_table("customer_details", _("Customer Details"), (str, str), ['key', 'val'], [_("Key"), _("Value")])
    form.add_table("supplier_details", _("Supplier Details"), (str, str), ['key', 'val'], [_("Key"), _("Value")])

    form.add_section(_("Financial Details"))
    form.add_text_field("currency", _("Currency"), default_value='$')
    form.add_text_field("vatname", _("VAT Name"), default_value=_('VAT'))
    form.add_text_field("vatpercent", _("VAT Percent"), default_value="21")
    form.add_number_field("serviceprice", _("Service Price (p/h)"))

    form.add_images_chooser("footer_images", _("Footer Images"))
    form.add_section(_("Styling Details"))
    form.add_color_chooser("bgcolor", _("Background Color"))
    form.add_color_chooser("accentcolor", _("Accent Color"))
    main_font = form.add_font_chooser("mainfont", _("Main Font"))
    main_font.set_filter_func(filter_mono, False)
    mono_font = form.add_font_chooser("monofont", _("Mono Font"))
    mono_font.set_filter_func(filter_mono, True)
    mono_font.set_font("Monospace")

    if data:
        form.load(data)

    return form


def open_profile(dialog, data=None, post_success=None):

    def _save_profile(_data):
        if save_profile(_data):
            if post_success:
                post_success(_data['profile_name'])
            dialog.set_transient_for(None)
            dialog.hide()

    dialog.set_modal(True)
    dialog.set_default_size(600, 400)
    form = get_create_profile_form(_save_profile, data=data)
    if data:
        form.fields['profile_name'].set_sensitive(False)
    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll.add(form)
    dialog.add(scroll)
    dialog.show_all()


class Profile(GObject.GObject):

    __gsignals__ = {
        'active_profile_changed': (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    # name = GObject.Property(type=str)
    # img = GObject.Property(type=Gtk.Image)

    def __init__(self, name, active):
        GObject.GObject.__init__(self)
        self.name = name
        self.active = active
        self.row = None
        self.img = None
        self.row_wrapper = None

    def create_row(self):
        self.row = Gtk.ListBoxRow()
        self.row_wrapper = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.row_wrapper.pack_start(Gtk.Label(label=self.name), True, False, 32)
        self.row.profile = self.name
        self.row.add(self.row_wrapper)
        self.img = Gtk.Image(stock=Gtk.STOCK_OK)
        if self.active:
            self.row_wrapper.pack_end(self.img, False, False, 8)
        self.row.show_all()
        return self.row

    def do_active_profile_changed(self, active_profile):
        was_active = self.active
        self.active = self.name == active_profile
        if not was_active and self.active:
            self.row_wrapper.pack_end(self.img, False, False, 8)
            self.img.show()
        elif was_active and not self.active:
            self.row_wrapper.remove(self.img)


def get_profiles_form():
    model = Gio.ListStore()
    list = Gtk.ListBox()

    list.bind_model(model, Profile.create_row)

    active_profile = get_preference("active_profile")
    for x in get_profiles():
        model.append(Profile(x, x == active_profile))

    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    hbox.pack_start(list, True, True, 0)
    buttons = Gtk.Box()
    buttons.set_orientation(Gtk.Orientation.VERTICAL)
    buttons.set_spacing(2)
    add_btn = Gtk.ToolButton()
    add_btn.set_icon_name("list-add")
    buttons.add(add_btn)
    edit_btn = Gtk.ToolButton()
    edit_btn.set_icon_widget(Gtk.Image(stock=Gtk.STOCK_EDIT))
    buttons.add(edit_btn)
    remove_btn = Gtk.ToolButton()
    remove_btn.set_icon_name("list-remove")
    buttons.add(remove_btn)
    activate_btn = Gtk.ToolButton()
    activate_btn.set_icon_widget(Gtk.Image(stock=Gtk.STOCK_OK))
    buttons.add(activate_btn)
    hbox.pack_start(buttons, False, True, 8)

    def select_active(*_args):
        selected = list.get_selected_row()
        set_preference("active_profile", selected.profile)

        for p in model:
            p.emit("active_profile_changed", selected.profile)

    def add_profile(*_args):
        profile_dialog = Gtk.Window(title=_("Add Profile"))

        def _add_profile(name):
            model.append(Profile(name, False))

        open_profile(profile_dialog, post_success=_add_profile)

    def edit_profile(*_args):
        selected = list.get_selected_row()
        profile_dialog = Gtk.Window(title=_("Edit Profile"))
        with open(get_profile(selected.profile), 'r') as pf:
            open_profile(profile_dialog, data=json.load(pf))

    def remove_profile(_btn):
        selected = list.get_selected_row()

        def handle_confirmation(widget, response):
            if response == Gtk.ResponseType.OK:
                list.remove(selected)
                os.remove(get_profile(selected.profile))
            widget.destroy()

        confirm_dialog = Gtk.MessageDialog(title=_("Remove Profile"),
                                           parent=_btn.get_ancestor(Gtk.Window),
                                           modal=True,
                                           destroy_with_parent=True,
                                           message_type=Gtk.MessageType.QUESTION,
                                           buttons=Gtk.ButtonsType.OK_CANCEL,
                                           text=_("Are you sure you want do delete the profile?"))
        confirm_dialog.connect("response", handle_confirmation)
        confirm_dialog.show()

    activate_btn.connect("clicked", select_active)
    add_btn.connect("clicked", add_profile)
    edit_btn.connect("clicked", edit_profile)
    remove_btn.connect("clicked", remove_profile)
    return hbox


if __name__ == '__main__':
    settings = Gtk.Settings.get_default()
    settings.props.gtk_button_images = True
    with open(get_profile('Default'), 'r') as f:
        profile = json.load(f)
    window = Gtk.Window()
    window.set_default_size(400, 600)
    window.connect("destroy", Gtk.main_quit)
    open_profile(window, data=profile)
    window.show_all()
    Gtk.main()
