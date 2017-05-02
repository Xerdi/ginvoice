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

from ginvoice.environment import image_dir

filename = 'generated_vars.tex'

cmd_template = '\\newcommand{\\%s}{%s}\n'
custom_cmd_template = '\\%s{%s}\n'
hours_template = '\t\\hourrow{%s}{%s}{%s}{%s}\n'
fee_template = '\t\\feerow{%s}{%s}{%s}{%s}\n'


def generate_addressee(f, data):
    f.write(cmd_template % ('addresseename', data['name']))
    f.write(cmd_template % ('addresseestreet', data['street']))
    f.write(cmd_template % ('addresseepostal', data['postal']))


def generate_records(f, data):
    rows_buffer = '%\n'
    for row in data:
        type = row['type']
        if type == 'hours':
            rows_buffer += hours_template % (row['client'], row['date'], row['description'], row['duration'])
        elif type == 'fee':
            rows_buffer += fee_template % (row['client'], row['date'], row['description'], row['costs'])
    f.write(cmd_template % ('records', rows_buffer))


def generate_supplier_info(f, data):
    f.write(cmd_template % ('invoicenr', data['invoice_nr']))
    f.write(custom_cmd_template % ('theauthor', data['author']))
    f.write(custom_cmd_template % ('thetitle', data['title']))
    f.write(custom_cmd_template % ('thesubtitle', data['subtitle']))

    def parse_map(key):
        return "\n" + "\n".join(["\t%s & %s \\\\" % (x['key'], x['val']) for x in data[key]]) + "\n"

    supplier_info = parse_map('supplier_details')
    f.write(cmd_template % ('supplierinfo', supplier_info))

    customer_info = parse_map('customer_details')
    f.write(cmd_template % ('customerinfo', customer_info))
    f.write("\n")


def generate_financial_details(f, data):
    f.write(custom_cmd_template % ('currency', data['currency']))
    f.write(custom_cmd_template % ('vatname', data['vatname']))
    f.write(custom_cmd_template % ('vatpercent', data['vatpercent']))
    f.write(custom_cmd_template % ('serviceprice', data['serviceprice']))
    f.write("\n")


def generate_styling(f, data):
    f.write("\\definecolor{bg}{HTML}{%s}\n" % data['bgcolor'])
    f.write("\\definecolor{accent}{HTML}{%s}\n" % data['accentcolor'])
    f.write("\\colorlet{headerbarcolor}{bg}\n")
    # f.write("\\arrayrulecolor{accent}\n")
    f.write("\n")
    if 'mainfont' in data:
        f.write("\\setmainfont{%s}\n" % data['mainfont'])
    if 'monofont' in data:
        f.write("\\setmonofont{%s}\n" % data['monofont'])
    f.write("\n")


def generate_ending(f, data):
    f.write(cmd_template % ('theending', data['ending']))
    f.write("\n")


def generate_images(f, data):
    f.write("\\graphicspath{{%s}}" % image_dir)
    if 'footer_images' in data:
        images = ["\t\\includegraphics[width=.1\\textwidth]{%s}\n" % x for x in data['footer_images']]
        f.write(cmd_template % ('images', '\n' + '\t\\hspace{1.5em}\n'.join(images)))
    f.write("\n")


def generate(user_info, addressee, records, path=""):
    with open(os.path.join(path, 'settings.tex'), 'w') as f:
        generate_supplier_info(f, user_info)
        generate_financial_details(f, user_info)
        generate_styling(f, user_info)
        generate_ending(f, user_info)
        generate_images(f, user_info)

    with open(os.path.join(path, filename), 'w') as f:
        generate_addressee(f, addressee)
        generate_records(f, records)


if __name__ == '__main__':
    user_data = None
    with (open("../../../src/basic_ginvoice_template/examples/supplier_defaults.json", "r")) as f:
        user_data = json.load(f)

    with (open("../../../src/basic_ginvoice_template/examples/invoice_request.json", "r")) as f:
        data = json.load(f)
        generate(
            user_data,
            data["addressee"],
            data["records"]
        )
