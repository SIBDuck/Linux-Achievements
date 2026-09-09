#!/usr/bin/env python3

# Copyright (C) 2026 SIBDuck
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Daemon that listens the terminal

import os
import atexit

with open("daemon.pid", "w") as f:
    f.write(str(os.getpid()))

def remove_pid():
    if os.path.exists("daemon.pid"):
        os.remove("daemon.pid")
atexit.register(remove_pid)


import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import variables as vars
import parsecmd
import pathlib
import subprocess

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(vars.PATH_LCMD):
            try:
                with open(vars.PATH_LCMD, "r", encoding="utf-8", errors="ignore") as f:
                    new_cmd = f.read().strip()
                if new_cmd and new_cmd != vars.cmd:
                    vars.cmd = new_cmd
                    parsecmd.parse()


            except FileNotFoundError:
                path_obj = pathlib.Path(vars.PATH_LCMD)
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.touch()

        elif os.path.abspath(event.src_path) == os.path.abspath(vars.PATH_EDITOR):
            try:
                with open(vars.PATH_EDITOR, "r", encoding="utf-8", errors="ignore") as f:
                    new_editor = f.read().strip()
                if new_editor and new_editor != vars.editor:
                    vars.editor = new_editor
            except FileNotFoundError:
                path_obj = pathlib.Path(vars.PATH_EDITOR)
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.touch()


def main():

    #print("Running...")
    path_obj = pathlib.Path(vars.PATH_LCMD)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    if not path_obj.exists():
        path_obj.touch()

    watch_dir = os.path.dirname(vars.PATH_LCMD)
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_dir, recursive=False)
    observer.daemon = True
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        #print("\nStopping...")
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
