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

from setuptools import setup
from subprocess import call
from glob import glob
from os.path import splitext, split

icon_resolutions = ["512", "256", "192", "128", "96", "64", "48", "42", "40", "32", "24", "22", "20", "16"]


def icon_map(res):
    return "share/icons/hicolor/%s/apps" % res, ["res/icon/%s/GinVoice.png" % res]


data_files = [
    ("share/applications", ["res/ginvoice.desktop"]),
    ("lib/ginvoice/templates", ["res/basic_template.tar.gz"])
]

for r in icon_resolutions:
    data_files.append(icon_map("%sx%s" % (r, r)))

po_files = glob("res/po/*.po")
for po_file in po_files:
    lang = splitext(split(po_file)[1])[0]
    mo_path = "locale/{}/LC_MESSAGES/ginvoice.mo".format(lang)
    call("mkdir -p locale/{}/LC_MESSAGES/".format(lang), shell=True)
    call("msgfmt {} -o {}".format(po_file, mo_path), shell=True)
    locales = map(lambda i: ('share/' + i, [i + '/ginvoice.mo', ]), glob('locale/*/LC_MESSAGES'))
    data_files.extend(locales)

setup(name="GinVoice",
      version=call("git describe --tags", shell=True),
      description="Creating LaTeX invoices with a GTK GUI",
      author="Erik Nijenhuis",
      author_email="erik@xerdi.com",
      license="GPLv3",
      packages=["ginvoice", "ginvoice.widgets"],
      data_files=data_files,
      install_requires=[
          "pycairo",
          "PyGObject",
          "xdg"
      ],
      entry_points={
          'console_scripts': ['ginvoice=ginvoice.app:main']
      })
