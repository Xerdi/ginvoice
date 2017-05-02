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
from gi.overrides import GdkPixbuf

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from ginvoice.i18n import _


def text_not_none(entry):
    return entry.get_text() != ''


class Form(Gtk.Box):
    prev_label = None

    def __init__(self, action=None, with_buttons=True) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.defaults = {}
        self.validators = {}
        self.action = action
        self.fields = {}
        self.field_list = Gtk.Grid()
        self.field_list.set_column_homogeneous(True)
        self.field_list.set_row_spacing(8)
        self.field_list.set_column_spacing(8)
        self.add(self.field_list)
        self.set_child_packing(self.field_list, True, True, 8, Gtk.PackType.START)
        if with_buttons:
            button_bar = Gtk.ActionBar()
            self.finish_button = Gtk.ToolButton()
            self.finish_button.set_icon_widget(Gtk.Image(stock=Gtk.STOCK_OK))
            self.finish_button.connect("clicked", self._on_action)
            button_bar.pack_end(self.finish_button)
            self.add(button_bar)
            self.set_child_packing(button_bar, False, False, 0, Gtk.PackType.END)

    def add_section(self, title):
        label = Gtk.Label(label=title)
        label.set_hexpand(True)
        hline = Gtk.HSeparator()
        hline.set_vexpand(False)
        if self.prev_label:
            self.field_list.attach_next_to(label, self.prev_label, Gtk.PositionType.BOTTOM, 4, 4)
        else:
            self.field_list.attach(label, 0, 0, 4, 4)
        self.field_list.attach_next_to(hline, label, Gtk.PositionType.BOTTOM, 4, 1)
        self.prev_label = hline

    def add_table(self, name, title, columns, column_names, column_titles):
        self.add_section(title)
        model = Gtk.ListStore(*columns)
        table = Gtk.TreeView(model=model)
        table.column_names = column_names
        table.set_reorderable(True)
        wrapper = Gtk.Box()
        wrapper.set_center_widget(table)
        for i, col in enumerate(column_titles):
            # TODO: map col types with renderer
            column = Gtk.TreeViewColumn(col, Gtk.CellRendererText(), text=i)
            column.set_min_width(100)
            table.append_column(column)
        if self.prev_label:
            self.field_list.attach_next_to(wrapper, self.prev_label, Gtk.PositionType.BOTTOM, 4, 4)
        else:
            self.field_list.attach(wrapper, 0, 0, 4, 4)
        toolbar = Gtk.Toolbar()
        add_btn = Gtk.ToolButton()
        add_btn.set_tooltip_text(_("Add Extra Company Information"))
        add_btn.set_icon_name("list-add")

        def add_table_record(*args):
            dialog = Gtk.Dialog(table.get_parent_window(), title=_("Add an Information Record"))
            dialog.set_modal(True)
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
            )
            box = dialog.get_content_area()

            def store_record(data):
                model.append(row=data.values())
                dialog.destroy()

            record_form = Form(with_buttons=False, action=store_record)
            for i2, col2 in enumerate(column_titles):
                # TODO: type mapping
                record_form.add_text_field(i2, col2)
            box.add(record_form)

            def _add_table_record(button, response):
                if response == Gtk.ResponseType.OK:
                    record_form._on_action(button)
                else:
                    dialog.destroy()

            dialog.connect("response", _add_table_record)
            dialog.show_all()

        add_btn.connect("clicked", add_table_record)
        toolbar.insert(add_btn, 1)
        remove_btn = Gtk.ToolButton()
        remove_btn.set_tooltip_text(_("Remove Extra Company Information"))
        remove_btn.set_icon_name("list-remove")

        def remove_table_record(*args):
            _model, _iter = table.get_selection().get_selected()
            if _iter:
                _model.remove(_iter)

        remove_btn.connect("clicked", remove_table_record)
        select = table.get_selection()

        def on_selection_change(s):
            _m, _i = s.get_selected()
            remove_btn.set_sensitive(_i is not None)

        select.connect("changed", on_selection_change)
        on_selection_change(select)
        toolbar.insert(remove_btn, 1)
        self.field_list.attach_next_to(toolbar, wrapper, Gtk.PositionType.BOTTOM, 4, 4)
        self.fields[name] = table
        self.prev_label = toolbar
        return table

    def add_text_field(self, name, title, default_value='', validator=None, tooltip=None):
        entry = Gtk.Entry()
        if tooltip:
            entry.set_tooltip_text(tooltip)
        self.defaults[name] = default_value
        entry.set_text(default_value)
        if validator:
            self.validators[name] = validator
        self._add_field(name, title, entry)
        return entry

    def add_number_field(self, name, title, default_value=None):

        def number_filter(entry, *args):
            text = entry.get_text().strip()
            entry.set_text(''.join([c for c in text if c in ',0123456789']))

        number_entry = Gtk.Entry()
        number_entry.connect('changed', number_filter)
        if default_value is not None:
            self.defaults[name] = default_value
            number_entry.set_text(str(default_value))
        self._add_field(name, title, number_entry)
        return number_entry

    def add_font_chooser(self, name, title):
        entry = Gtk.FontButton()
        entry.set_title(title)
        entry.set_use_size(False)
        entry.set_show_size(False)
        self._add_field(name, title, entry)
        return entry

    def add_color_chooser(self, name, title, default_value="#FFFFFF"):
        entry = Gtk.ColorButton()
        entry.set_use_alpha(False)
        entry.set_title(title)
        # set default color
        self.defaults[name] = default_value
        color = Gdk.RGBA()
        color.parse(default_value)
        entry.set_rgba(color)
        self._add_field(name, title, entry)
        return entry

    def add_images_chooser(self, name, title):
        self.add_section(title)
        wrapper = Gtk.Box()
        wrapper.set_orientation(Gtk.Orientation.VERTICAL)
        model = Gtk.ListStore(GdkPixbuf.Pixbuf)
        button_group = Gtk.ActionBar()

        column = Gtk.TreeViewColumn(title, Gtk.CellRendererPixbuf(), pixbuf=0)
        entry = Gtk.TreeView(model=model)

        def handle_select_image(_btn):
            fn = _btn.get_filename()
            _btn.unselect_all()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(fn, 100, 100, True)
            model.append(row=[pixbuf])

        def handle_remove_image(_btn):
            _model, _iter = entry.get_selection().get_selected()
            if _iter:
                _model.remove(_iter)

        add_btn = Gtk.FileChooserButton.new(title, Gtk.FileChooserAction.OPEN)
        add_btn.connect("file-set", handle_select_image)
        remove_btn = Gtk.ToolButton()
        remove_btn.set_icon_name("list-remove")
        remove_btn.connect("clicked", handle_remove_image)
        button_group.add(add_btn)
        button_group.add(remove_btn)
        entry.append_column(column)
        wrapper.set_center_widget(entry)
        wrapper.pack_end(button_group, False, False, 0)
        self.field_list.attach_next_to(wrapper, self.prev_label, Gtk.PositionType.BOTTOM, 4, 4)
        self.fields[name] = entry
        self.prev_label = wrapper
        return entry

    def add_switch(self, name, title):
        switch = Gtk.Switch()
        switch.set_halign(Gtk.Align.START)
        self._add_field(name, title, switch)
        return switch

    def clear(self, button):
        for key, entry in self.fields.items():
            if isinstance(entry, Gtk.FontButton):
                entry.set_font("Sans")
            elif isinstance(entry, Gtk.ColorButton):
                color = Gdk.RGBA()
                color.parse(self.defaults[key])
                entry.set_rgba(color)
            elif isinstance(entry, Gtk.TreeView):
                entry.get_model().clear()
            else:
                if key in self.defaults:
                    entry.set_text(self.defaults[key])
                else:
                    entry.set_text('')

    def load(self, data):
        for title, entry in self.fields.items():
            if isinstance(entry, Gtk.FontButton):
                entry.set_font_name(data[title])
            elif isinstance(entry, Gtk.ColorButton):
                c = Gdk.RGBA()
                c.parse(data[title])
                entry.set_rgba(c)
            elif isinstance(entry, Gtk.TreeView):
                model = entry.get_model()
                if title in data:
                    for r in data[title]:
                        model.append(row=r.values())
            else:
                entry.set_text(data[title])

    def _add_field(self, name, title, field):
        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.END)
        label.set_margin_start(8)
        if self.prev_label:
            self.field_list.attach_next_to(label, self.prev_label, Gtk.PositionType.BOTTOM, 1, 1)
        else:
            self.field_list.attach(label, 0, 0, 1, 1)
        field.set_margin_end(8)
        self.field_list.attach_next_to(field, label, Gtk.PositionType.RIGHT, 3, 1)
        self.fields[name] = field
        self.prev_label = label

    def _on_action(self, button):
        is_valid = True
        for k, v in self.validators.items():
            entry = self.fields[k]
            if not v(entry):
                # https://askubuntu.com/questions/252062/highlighting-gtk-entry-fields-on-invalid-input-by-user
                # entry.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("red"))
                if is_valid:
                    entry.grab_focus()
                is_valid = False

        if is_valid:
            if self.action is not None:
                self.action(self._fields_to_value())
            else:
                print("Warning: no action mapped to form")
            self.clear(button)

    def _fields_to_value(self):
        result = {}
        for title, entry in self.fields.items():
            if isinstance(entry, Gtk.FontButton):
                result[title] = entry.get_font_family().get_name()
            elif isinstance(entry, Gtk.ColorButton):
                color = entry.get_rgba()
                result[title] = "#" + "".join(["%02x" % int(c * 255) for c in [color.red, color.green, color.blue]])
            elif isinstance(entry, Gtk.TreeView):
                model = entry.get_model()
                result[title] = []
                for r in model:
                    record = {}
                    for i, k in enumerate(entry.column_names):
                        record[k] = r[i]
                    result[title].append(record)
            else:
                result[title] = entry.get_text()
        return result


if __name__ == '__main__':
    window = Gtk.Window()
    window.set_default_size(-1, -1)
    window.connect("destroy", Gtk.main_quit)

    form = Form()
    for idx in range(0, 5):
        form.add_text_field("%d" % idx, "Field %d" % idx)

    window.add(form)
    window.show_all()
    Gtk.main()
