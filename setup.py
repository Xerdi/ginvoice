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
import os
import subprocess


def get_version():
    # Prefer explicit version passed from packaging environment
    v = os.getenv("GINVOICE_VERSION")
    if v:
        return v
    # Try to infer from git tags if available
    try:
        out = subprocess.check_output(["git", "describe", "--tags"])  # nosec - local meta query
        return out.decode("utf-8").split("-")[0]
    except Exception:
        # Fallback to a sane default when no git metadata is present
        return "0.0.0"


setup(
    name="GinVoice",
    version=get_version(),
    description="Creating LaTeX invoices with a GTK GUI",
    author="Erik Nijenhuis",
    author_email="erik@xerdi.com",
    license="GPLv3",
    packages=["ginvoice", "ginvoice.ui", "ginvoice.model"],
    entry_points={
        'console_scripts': ['ginvoice=ginvoice.main:main', 'gingen=ginvoice.generator:main']
    }
)
