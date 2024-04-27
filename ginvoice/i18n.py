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

import gettext, locale, os

from ginvoice.environment import get_locale_dir

APP_NAME = 'ginvoice'


def update_locale(new_locale):
    locale_dir = get_locale_dir()
    if new_locale:
        new_locale += ".UTF-8"
        os.environ['LANG'] = new_locale
        os.environ['LANGUAGE'] = new_locale[:2]
        locale.setlocale(locale.LC_ALL, new_locale)

    try:
        locale.bindtextdomain(APP_NAME, locale_dir)
        locale.textdomain(APP_NAME)
    except:
        pass

    gettext.bindtextdomain(APP_NAME, locale_dir)
    gettext.textdomain(APP_NAME)
    gettext.install(APP_NAME, locale_dir)


_ = gettext.gettext
