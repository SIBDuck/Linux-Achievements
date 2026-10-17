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



import json
import pathlib
import re
import shlex
import sys
import variables as v

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from achievement_manager import notifications
class Parser:
    @staticmethod
    def paths():
        BASE_DIR = pathlib.Path(__file__).resolve().parent
        NEIGHBOR_DIR = BASE_DIR.parent / "data"

        ACHIEVMENTS_PATH = NEIGHBOR_DIR / "achievements.json"
        DATA_PATH = NEIGHBOR_DIR / "player data.json"
        return (ACHIEVMENTS_PATH, DATA_PATH)

    @staticmethod
    def parse_list():
        v.parsed = re.sub(r'\b--color=auto\b', "", v.cmd)
        # Parses to [data, command (may consist of a few elements (el1, el2...), success code (0 or 1))]
        v.parsed = shlex.split(v.parsed)
        #vars.utm = vars.parsed[0]
        # parse_time(vars.utm)
        #print(vars.parsed)

    @staticmethod
    def find_re(pcmd: list, RE, ach_mt):
        cmd = " ".join(str(arg) for arg in pcmd[2:]).strip()
        return re.search(RE, cmd, re.IGNORECASE) and not ach_mt["done"]

