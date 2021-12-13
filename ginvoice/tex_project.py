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
import threading

import gi
import os
import subprocess
import tarfile
import tempfile

from ginvoice.environment import get_templates, tex_dir

from ginvoice.model.preference import preference_store

gi.require_version("Gtk", "3.0")
from gi.repository import GObject


def get_members(tar, prefix):
    if not prefix.endswith('/'):
        prefix += '/'
    offset = len(prefix)
    for tarinfo in tar.getmembers():
        if tarinfo.name.startswith(prefix):
            tarinfo.name = tarinfo.name[offset:]
            yield tarinfo


class TexProject(GObject.GObject):

    __gsignals__ = {
        'pdfviewer_exited': (GObject.SignalFlags.RUN_FIRST, None, (int,))
    }

    latexmk_proc = None
    previewer_proc = None

    def __init__(self, working_directory=None, template_selection='basic_template'):
        GObject.GObject.__init__(self)
        self.working_directory = working_directory
        if not self.working_directory:
            self.working_directory = tempfile.mkdtemp(prefix=os.path.join(tex_dir, ''))
            template_tar = get_templates()[0]
            template = tarfile.open(template_tar)
            template.extractall(self.working_directory, members=get_members(template, template_selection))
            template.close()
            print("Created tex directory %s" % self.working_directory)

    def run_tex(self, run_once=True):
        self.stop_tex()
        self._latexmk(run_once)

    def stop_tex(self):
        if self.latexmk_proc and self.latexmk_proc.poll() is None:
            self.latexmk_proc.kill()

    def _latexmk(self, run_once):
        cmd = ['latexmk', '-f', '-lualatex', '--shell-escape', '-interaction=nonstopmode']
        if not run_once:
            cmd.append('-pvc')
        cmd.append('main')
        self.latexmk_proc = subprocess.Popen(cmd, cwd=self.working_directory,
                                             stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL,
                                             shell=False)
        if run_once:
            return_code = self.latexmk_proc.wait()
            if return_code:
                print("ERROR: Latexmk exited with code %d" % return_code)
                subprocess.Popen(['xdg-open', os.path.join(self.working_directory, 'main.log')])
            self.latexmk_proc = None
        else:
            if self.latexmk_proc.poll() is not None:
                print("ERROR: Latexmk exited with code %d" % self.latexmk_proc.poll())
                subprocess.Popen(['xdg-open', os.path.join(self.working_directory, 'main.log')])
                self.latexmk_proc = None

    def clear(self):
        self.stop_previewer()
        subprocess.Popen(['latexmk', '-C'], cwd=self.working_directory,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    def run_previewer(self):
        self.stop_previewer()
        self._previewer()

    def stop_previewer(self):
        if self.previewer_proc and self.previewer_proc.poll() is None:
            self.previewer_proc.kill()

    def _previewer(self):
        self.previewer = preference_store['pdf_viewer'].value
        if self.previewer:
            self.previewer_proc = subprocess.Popen([self.previewer, 'main.pdf'], cwd=self.working_directory)
            self._watch_process(self.previewer_proc)
        else:
            subprocess.Popen(['xdg-open', os.path.join(self.working_directory, 'main.pdf')])

    def _watch_process(self, proc):
        def watcher(_self, _proc):
            _self.emit('pdfviewer_exited', _proc.wait())

        threading.Thread(target=watcher, args=(self, proc)).start()

