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
from subprocess import check_output

setup(name="GinVoice",
      version=check_output("git describe --tags", shell=True).decode('utf-8').split('-')[0],
      description="Creating LaTeX invoices with a GTK GUI",
      author="Erik Nijenhuis",
      author_email="erik@xerdi.com",
      license="GPLv3",
      packages=["ginvoice", "ginvoice.ui", "ginvoice.model"],
      entry_points={
          'console_scripts': ['ginvoice=ginvoice.main:main', 'gingen=ginvoice.generator:main']
      })
