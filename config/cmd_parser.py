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

