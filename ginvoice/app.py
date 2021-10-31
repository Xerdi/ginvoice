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
import shutil
import subprocess
import tarfile

import gi
from gi.overrides.Gdk import Gdk
from gi.overrides.Gio import Gio

from ginvoice.preferences import get_preference, set_preference
from ginvoice.profile import get_create_profile_form, save_profile, increment_invoice, get_profiles_form, open_profile

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from ginvoice.widgets.sidebar import Sidebar
from ginvoice.customers import CustomerController
# from ginvoice.generator import generate
from ginvoice.environment import invoice_nr_file, setup_environment, get_templates, tex_dir, get_client_template_dir, \
    get_client_templates, get_profile, load_profile
from ginvoice.i18n import _

title = _("Invoicing")
window = Gtk.Window(title=title)

screen = Gdk.Screen.get_default()
provider = Gtk.CssProvider()
style_context = Gtk.StyleContext()
style_context.add_provider_for_screen(
    screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)
css = b"""
headerbar separator {
    margin-top: 0;
    margin-bottom: 0;
}
"""
provider.load_from_data(css)

header_bar = Gtk.HeaderBar()
header_bar.set_show_close_button(True)
header_bar.props.title = title
window.set_titlebar(header_bar)

left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
left_box.set_size_request(226, -1)
right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

search_entry = Gtk.Entry()
search_button = Gtk.ToggleButton()
search_icon = Gio.ThemedIcon(name="system-search-symbolic")
search_image = Gtk.Image.new_from_gicon(
    search_icon, Gtk.IconSize.BUTTON)
search_button.set_tooltip_text(_("Search"))
search_button.set_image(search_image)

settings_popover = Gtk.Popover()
preferences_button = Gtk.ModelButton(label="Active Profile")
profiles_button = Gtk.ModelButton(label="Profiles")
vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
vbox.pack_start(profiles_button, False, False, 4)
vbox.pack_start(preferences_button, False, False, 4)
vbox.show_all()
settings_popover.add(vbox)
settings_popover.set_position(Gtk.PositionType.BOTTOM)

settings_button = Gtk.MenuButton(popover=settings_popover)
settings_icon = Gio.ThemedIcon(name="open-menu-symbolic")
settings_image = Gtk.Image.new_from_gicon(settings_icon, Gtk.IconSize.BUTTON)
settings_button.set_image(settings_image)

left_box.pack_start(search_button, False, False, 0)
# right_box.pack_start(search_entry, False, False, 8)
# left_box.pack_end(Gtk.SeparatorMenuItem(), False, False, 8)
left_box.pack_end(settings_button, False, False, 0)

header_bar.pack_start(left_box)
separator = Gtk.SeparatorMenuItem()
separator.set_margin_top(0)
separator.set_margin_bottom(0)
header_bar.pack_start(separator)
header_bar.pack_end(right_box)


def ensure_tex_dir(client):
    client_dir = os.path.join(tex_dir, client)
    template_tar = get_templates()[0]
    if not os.path.exists(client_dir):
        os.mkdir(client_dir)
    if len(get_client_templates(client)) == 0:
        template = tarfile.open(template_tar)
        template.extractall(client_dir)
        template.close()
        # TODO prompt templates and fix preferences
    return get_client_template_dir(client)


def gen_add_record(record_type, record_store):
    def add_record(record):
        record_store.append(row=[
            record_type,
            record[_("Client")],
            record[_("Date")],
            record[_("Description")],
            int(record[_("Value")])
        ])

    return add_record


def parse_record(table_row):
    record = {}
    is_hours_type = table_row[0] == _('Minutes')
    if is_hours_type:
        record["type"] = "hours"
    else:
        record["type"] = "fee"
    record["client"] = table_row[1]
    record["date"] = table_row[2]
    record["description"] = table_row[3]
    if is_hours_type:
        record["duration"] = table_row[4]
    else:
        record["costs"] = table_row[4]
    return record


def gen_create_pdf(addressee_func, record_store_provider):
    def create_pdf(button):
        addressee = addressee_func()
        working_dir = ensure_tex_dir(addressee['name'])
        profile = load_profile(get_preference('active_profile'))
        records = []
        record_store = record_store_provider()
        for record in record_store:
            records.append(parse_record(record))
        generate(profile, addressee, records, working_dir)

        tex_proc = subprocess.Popen(["latexmk", "--shell-escape", "-lualatex", "-interaction=nonstopmode", "main"],
                                    cwd=working_dir,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        tex_proc.communicate()
        if tex_proc.returncode:
            def close_on_action(widget, response):
                if response == Gtk.ResponseType.OK:
                    subprocess.Popen(["xdg-open", "main.log"],
                                     cwd=working_dir,
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                widget.destroy()

            error_dialog = Gtk.MessageDialog(parent=window,
                                             message_type=Gtk.MessageType.ERROR,
                                             buttons=Gtk.ButtonsType.OK_CANCEL,
                                             text=_("An error occurred when creating the PDF file. Show the log?"))
            error_dialog.connect("response", close_on_action)
            error_dialog.show()
            return

        # TODO get viewer get_preference("pdf_previewer")
        viewer_proc = subprocess.Popen(["evince", "main.pdf"], cwd=working_dir)

        def handle_confirmation(widget, response):
            viewer_proc.kill()
            if response == Gtk.ResponseType.OK:

                save_dialog = Gtk.FileChooserDialog(title=_("Save"),
                                                    parent=window,
                                                    action=Gtk.FileChooserAction.SAVE)
                save_dialog.set_default_response(Gtk.ResponseType.ACCEPT)
                save_dialog.set_local_only(False)
                save_dialog.add_button(_("Save"), Gtk.ResponseType.ACCEPT)
                save_dialog.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)
                save_dialog.set_current_name("%s %s.pdf" % (_("Invoice"), profile["invoice_nr"]))
                save_dialog.set_current_folder(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOCUMENTS))
                save_dialog.show()
                save_response = save_dialog.run()
                if save_response == Gtk.ResponseType.ACCEPT:
                    increment_invoice()

                    shutil.copyfile(os.path.join(working_dir, "main.pdf"), save_dialog.get_filename())
                    record_store.clear()
                save_dialog.destroy()

            widget.destroy()

        confirm_dialog = Gtk.MessageDialog(title=_("Verification"),
                                           parent=window,
                                           modal=True,
                                           destroy_with_parent=True,
                                           message_type=Gtk.MessageType.QUESTION,
                                           buttons=Gtk.ButtonsType.OK_CANCEL,
                                           text=_("PDF created. Continue?"))
        confirm_dialog.connect("response", handle_confirmation)
        confirm_dialog.show()

    return create_pdf


window.set_default_size(800, 600)

main_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
window.add(main_layout)

sidebar = Sidebar(min_width=240)
main_layout.add(sidebar)

customer_controller = CustomerController(sidebar)

toolbar = Gtk.ActionBar()
list_add_button = Gtk.ToolButton()
list_add_button.set_tooltip_text(_("Add Customer"))
list_add_button.set_icon_name("list-add")
list_add_button.connect("clicked", customer_controller.on_create)
toolbar.add(list_add_button)
list_remove_button = Gtk.ToolButton()
list_remove_button.set_tooltip_text(_("Remove Customer"))
list_remove_button.set_icon_name("list-remove")
list_remove_button.connect("clicked", customer_controller.on_destroy)
toolbar.add(list_remove_button)
list_edit_button = Gtk.ToolButton()
list_edit_button.set_tooltip_text(_("Edit Customer"))
list_edit_button.set_icon_widget(Gtk.Image(stock=Gtk.STOCK_EDIT))
list_edit_button.connect("clicked", customer_controller.on_edit)
toolbar.add(list_edit_button)
main_layout.add(toolbar)

pdf_button = Gtk.ToolButton()
pdf_button.set_icon_name("document-save")
pdf_button.set_tooltip_text(_("Create Invoice"))
pdf_button.connect("clicked", gen_create_pdf(addressee_func=customer_controller.get_customer_details,
                                             record_store_provider=customer_controller.get_current_record_store))
toolbar.pack_end(pdf_button)
window.connect("destroy", Gtk.main_quit)
window.show_all()


def open_default_profile(*_args):
    profile_dialog = Gtk.Window(title=_("Edit Default Profile"))
    with open(get_profile(get_preference("active_profile")), 'r') as f:
        open_profile(profile_dialog, data=json.load(f))


def open_profiles(*_args):
    dialog = Gtk.Window(title=_("Profiles"))
    dialog.set_transient_for(window)
    dialog.set_default_size(450, 300)
    dialog.set_modal(True)
    dialog.add(get_profiles_form())
    dialog.show_all()


profiles_button.connect("clicked", open_profiles)
preferences_button.connect("clicked", open_default_profile)


def main():
    setup_environment()
    active_profile = get_preference("active_profile")
    if not active_profile or not os.path.exists(get_profile(active_profile)):
        profile_dialog = Gtk.Window(title=_("Create a Profile"))
        profile_dialog.connect("destroy", Gtk.main_quit)
        profile_dialog.set_transient_for(window)

        def set_profile_active(name):
            set_preference("active_profile", name)
        open_profile(profile_dialog, post_success=set_profile_active)

    Gtk.main()


if __name__ == '__main__':
    main()
