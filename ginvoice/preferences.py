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

import os, json
from ginvoice.environment import preferences_file


preference_keys = ["active_profile"]
preference_cache = None


def _get_preference_data():
    global preference_cache
    if not preference_cache and os.path.exists(preferences_file):
        with open(preferences_file, "r") as f:
            preference_cache = json.load(f)
    return preference_cache


def _save_preference_data(data):
    with open(preferences_file, "w") as f:
        json.dump(data, f)


def get_preference(key):
    if key not in preference_keys:
        raise 'No such preference key'
    data = _get_preference_data()
    if key in data:
        return data[key]
    return None


def set_preference(key, val):
    if key not in preference_keys:
        raise 'No such preference key'
    data = _get_preference_data()
    data[key] = val
    _save_preference_data(data)


if __name__ == '__main__':
    pass
