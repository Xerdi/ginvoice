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

from ginvoice.model.column import TableColumnStore, CumulativeColumnStore
from ginvoice.i18n import _
from ginvoice.model.preference import preference_store as ps
from ginvoice.generator import GENERATORS, format_tex
from ginvoice.model.customer import Customer
from ginvoice.environment import customer_info_file, supplier_info_file
from ginvoice.gtk import GObject, Gtk


class Document(GObject.GObject):
    customer = GObject.Property(type=Customer)

    def __init__(self, customer: Customer,
                 table_col: TableColumnStore,
                 cum_col: CumulativeColumnStore,
                 record_store: Gtk.ListStore,
                 ending: Gtk.Entry,
                 totals: list, working_dir: str):
        GObject.GObject.__init__(self)
        self.customer = customer
        self.table_col = table_col
        self.cum_col = cum_col
        self.record_store = record_store
        self.ending = ending
        self.totals = totals
        self.working_dir = working_dir

    def set_data(self, section, data, filename=None):
        if not filename:
            filename = section + '.tex'
        path = os.path.join(self.working_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            GENERATORS[section](f, data)

    def parse_columns(self):
        types = ["L", "R", "L", "F", "F", "F", "F", "F"]
        result = []
        for idx, x in enumerate(self.table_col):
            stype = x.size_type
            if stype == 1:
                result.append({
                    "title": x.title,
                    "type": types[idx],
                    "width": 1.0
                })
            elif stype == 2:
                result.append({
                    "title": x.title,
                    "type": types[idx],
                    "width": x.text
                })
        return result

    def parse_records(self):
        result = []
        for r in self.record_store:
            row = []
            if self.table_col[0].size_type != 0:
                row.append(r[8].description)
            if self.table_col[1].size_type != 0:
                row.append(r[8].date)
            if self.table_col[2].size_type != 0:
                row.append(r[8].quantity_format())
            if self.table_col[3].size_type != 0:
                row.append(r[8].price)
            if self.table_col[4].size_type != 0:
                row.append(r[8].discount)
            if self.table_col[5].size_type != 0:
                row.append(r[8].subtotal)
            if self.table_col[6].size_type != 0:
                row.append(r[8].vat)
            if self.table_col[7].size_type != 0:
                row.append(r[8].total)
            result.append(row)
        return result

    def parse_cumulatives(self):
        result = []
        for idx, c in enumerate(self.cum_col):
            if c.size_type != 0:
                result.append({
                    "key": c.title,
                    "val": self.totals[idx]
                })
        return result

    def reload(self, _vars):
        self.set_data('languages', [ps['babel'].value])
        self.set_data('header', {
            "subtitle": ps['subtitle'].value
        })
        self.set_data('addressee', format_tex(self.customer.addresslines).split(os.linesep))
        with open(customer_info_file) as fp:
            self.set_data('customer_info',
                          [{'key': v['key'], 'val': v['val'].format_map(_vars)} for v in json.load(fp)])
        with open(supplier_info_file) as fp:
            self.set_data('supplier_info',
                          [{'key': v['key'], 'val': v['val'].format_map(_vars)} for v in json.load(fp)])
        self.set_data('table', {
            "columns": self.parse_columns(),
            "cumulative": self.parse_cumulatives(),
            "records": self.parse_records()
        })
        self.set_data('footer', {
            "ending": self.ending.get_text().format_map(_vars),
            "images": [x for x in
                       [
                           ps['footer_image_1'].value,
                           ps['footer_image_2'].value,
                           ps['footer_image_3'].value
                       ] if x is not None]
        })
        self.set_data('style', {
            "main_font": ps['main_font'].value,
            "mono_font": ps['mono_font'].value,
            "background_color": ps['background_color'].value,
            "accent_color": ps['foreground_color'].value,
            "style_table": False
        })
        self.set_data('misc', {
            "currency": ps['currency'].value,
            "author": ps['author'].value,
            "title": ps['title'].value,
            "subject": ps['subtitle'].value,
            "keywords": ps['keywords'].value,
            "producer": "GinVoice Generator",
            "creator": "gingen",
            "continuationheader": "\\title{} -- \\subject{}",
            "continuationfooter": _("See next page"),
        }, "meta.tex")
