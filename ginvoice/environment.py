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

import os
from xdg.BaseDirectory import (
    xdg_cache_home,
    xdg_config_dirs,
    xdg_config_home,
    xdg_data_dirs,
    xdg_data_home
)

app_name = 'ginvoice'

config_dir = os.path.join(xdg_config_home, app_name)
data_dir = os.path.join(xdg_data_home, app_name)
tex_dir = os.path.join(xdg_cache_home, app_name)
preferences_file = os.path.join(config_dir, "preferences.json")
image_dir = os.path.join(data_dir, 'img')

template_dirs = [x for x in [os.path.join(data_dir, "templates"),
                             "/usr/lib/ginvoice/templates",
                             "/usr/local/lib/ginvoice/templates"]
                 if os.path.exists(x)]

res_dirs = [
    "/lib/ginvoice",
    "/usr/lib/ginvoice",
    "/usr/local/lib/ginvoice"
]

customer_file = os.path.join(config_dir, 'customers.json')
customer_info_file = os.path.join(config_dir, 'customer_info.json')
supplier_info_file = os.path.join(config_dir, 'supplier_info.json')
table_column_file = os.path.join(config_dir, 'table.json')
cumulative_column_file = os.path.join(config_dir, 'cumulatives.json')


def setup_environment():
    for directory in [config_dir, data_dir, tex_dir, image_dir]:
        if not os.path.exists(directory):
            os.mkdir(directory)
    for file, text in [
        (preferences_file, "{}"),
        (customer_file, "[]"),
        (customer_info_file, "[]"),
        (supplier_info_file, "[]"),
        (table_column_file, "[]"),
        (cumulative_column_file, "[]")]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write(text)


def get_templates():
    templates = []
    for template_dir in template_dirs:
        templates += [os.path.join(template_dir, x) for x in os.listdir(template_dir) if
                      x.endswith('.tar.gz')]
    return templates


def get_image(filename):
    return os.path.join(image_dir, filename)


def get_images():
    return [os.path.basename(x) for x in os.listdir(image_dir)]


def get_resource(file):
    for p in res_dirs:
        path = os.path.join(p, file)
        if os.path.exists(path):
            return path


if __name__ == '__main__':
    setup_environment()
    print("Config dir", config_dir)
    print("Data dir", data_dir)
    print("Tex dir", data_dir)
    print("Template dir", template_dirs)
    print("Customer file", customer_file)
    print("Preferences file", preferences_file)
    print("Image dir", image_dir)
    print("Current images", get_images())
    print("Data dirs", xdg_data_dirs())
