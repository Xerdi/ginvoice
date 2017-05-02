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
from xdg import (
    xdg_cache_home,
    xdg_config_dirs,
    xdg_config_home,
    xdg_data_dirs,
    xdg_data_home
)

app_name = 'ginvoice'

config_dir = os.path.join(str(xdg_config_home()), app_name)
data_dir = os.path.join(str(xdg_data_home()), app_name)
tex_dir = os.path.join(str(xdg_cache_home()), app_name)
profile_dir = os.path.join(config_dir, "profiles")
preferences_file = os.path.join(config_dir, "preferences.json")
image_dir = os.path.join(data_dir, 'img')

template_dirs = [x for x in [os.path.join(data_dir, "templates"),
                             "/usr/lib/ginvoice/templates",
                             "/usr/local/lib/ginvoice/templates"]
                 if os.path.exists(x)]

invoice_nr_file = os.path.join(config_dir, 'invoice_nr.txt')
customer_file = os.path.join(config_dir, 'customers.json')


def setup_environment():
    for directory in [config_dir, data_dir, tex_dir, image_dir, profile_dir]:
        if not os.path.exists(directory):
            os.mkdir(directory)


def get_templates():
    templates = []
    for template_dir in template_dirs:
        templates += [os.path.join(template_dir, x) for x in os.listdir(template_dir) if
                      x.endswith('.tar.gz')]
    return templates


def get_client_templates(client):
    client_dir = os.path.join(tex_dir, client)
    return [os.path.join(client_dir, x) for x in os.listdir(client_dir) if os.path.isdir(os.path.join(client_dir, x))]


def get_client_template_dir(client):
    # TODO parse (client) preferences
    return get_client_templates(client)[0]


def get_profile(name):
    return os.path.join(profile_dir, "%s.json" % name)


def get_profiles():
    return [x[:-5] for x in os.listdir(profile_dir) if x.endswith(".json")]


def get_image(filename):
    return os.path.join(image_dir, filename)


def get_images():
    return [os.path.basename(x) for x in os.listdir(image_dir)]


def load_profile(name):
    with open(get_profile(name), 'r') as f:
        return json.load(f)


if __name__ == '__main__':
    setup_environment()
    print("Config dir", config_dir)
    print("Data dir", data_dir)
    print("Tex dir", data_dir)
    print("Template dir", template_dirs)
    print("Invoice path", invoice_nr_file)
    print("Customer file", customer_file)
    print("Profile dir", profile_dir)
    print("Preferences file", preferences_file)
    print("Image dir", image_dir)
    print("Current images", get_images())
