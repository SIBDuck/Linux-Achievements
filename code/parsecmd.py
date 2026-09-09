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



import shlex
import variables as vars
import time
import re
from datetime import datetime, timezone
import time
import json
import notifications
import os


def parse_list():
    vars.parsed = re.sub(r'--color=auto', "", vars.cmd)
    # Parses to [data, command (may consist of a few elements (el1, el2...), success code (0 or 1))]
    vars.parsed = shlex.split(vars.parsed)
    vars.utm = vars.parsed[0]
    # parse_time(vars.utm)
    print(vars.parsed)


def parse_time(date: str):
    date = date.replace("_", " ")
    date = date.replace(".", " ")
    date = date.replace(":", " ")
    date = date.split(" ")
    dt = datetime(int(date[2]), int(date[1]), int(date[0]), int(date[3]), int(date[4]), int(date[5]),
                  tzinfo=timezone.utc)
    ms_utc = int(dt.timestamp() * 1000)
    vars.parsed[0] = ms_utc


def vim_timecount(pcmd: list):
    status = pcmd[1]
    current_time = pcmd[0]
    if status == "START":
        vars.vim_tm1 = current_time
        return
    if status == "END":
        vars.vim_tm2 = current_time
        vars.vim_time_s += (vars.vim_tm2 - vars.vim_tm1)
        vars.vim_time_ = vim_time_conv(vars.vim_time_s)

        with open("data/player data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        data["stats"]["time"]["vim"] = vars.vim_time_s

        with open("data/player data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def vim_detector(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    cmd = " ".join(str(arg) for arg in pcmd).strip()

    if re.search(vars.vim_find_re, cmd, re.IGNORECASE):
        vim_timecount(vars.parsed)


def vi_detector(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    ach = "vim.open.vi"
    ach_meta = data["achievements"]["en"][ach]

    if find_re(pcmd, vars.vi_find_re, ach_meta) and pcmd[-1] == "0":
        do(data, ach, ach_meta, vars.open_vi_flag, vars)

    write_ach(data, vars.open_vi_flag,vars)


def vim_time_conv(time: int):
    # Converts time spent in vim from seconds into hours and minutes respectively
    return [time / 3600, time / 60]


def vim_time_achv(time: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    with open("data/achievements.json", "r", encoding="utf-8") as f:
        achvs = json.load(f)

    # Unpack the list directly into hours and minutes
    hours = time[0]
    minutes = time[1]

    # Mapping layout updated to check the correct index types:
    # (time_value, variable_to_check, achievement_id)
    stockholm_thresholds = [
        (10, minutes, "vim.time.stockholm.1"),  # 10 minutes
        (30, minutes, "vim.time.stockholm.2"),  # 30 minutes
        (1, hours, "vim.time.stockholm.3"),  # 1 hour
        (5, hours, "vim.time.stockholm.4"),  # 5 hours
        (10, hours, "vim.time.stockholm.5"),  # 10 hours
        (24, hours, "vim.time.stockholm.6"),  # 24 hours
        (50, hours, "vim.time.stockholm.7"),  # 50 hours
        (100, hours, "vim.time.stockholm.8"),  # 100 hours
        (500, hours, "vim.time.stockholm.9"),  # 500 hours
        (1000, hours, "vim.time.stockholm.10"),  # 1000 hours
    ]

    # Process milestones (safe for single or sequential multi-unlocks)
    for threshold, current_value, ach_id in stockholm_thresholds:
        if current_value >= threshold and not data["achievements"][ach_id]["done"]:
            ach_meta = achvs["achievements"]["en"][ach_id]

            # Mark as unlocked in the player profile tracker
            data["achievements"][ach_id]["done"] = True

            # Display the alert using your corrected JSON keys
            do(data, ach_id, ach_meta, vars.vim_time_flag, vars)

    write_ach(data, vars.vim_time_flag,vars)


def poweroff_reboot_check(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    with open("data/achievements.json", "r", encoding="utf-8") as f:
        achvs = json.load(f)

    poweroff_reboot_thresholds = [
        "sh.poweroff",
        "sh.reboot"
    ]

    for ach in poweroff_reboot_thresholds:
        ach_meta = achvs["achievements"]["en"][ach]

        if ach == "sh.poweroff":
            if find_re(pcmd, vars.poweroff_find_re, ach_meta) and pcmd[-1] == "1":
                do(data, ach, ach_meta, vars.poweroff_reboot_flag, vars)

        else:
            if find_re(pcmd, vars.reboot_find_re, ach_meta) and pcmd[-1] == "1":
                do(data, ach, ach_meta, vars.poweroff_reboot_flag,vars)
    if vars.poweroff_reboot_flag:
        write_ach(data, vars.poweroff_reboot_flag,vars)

    if vars.poweroff_reboot_flag:
        with open("data/achievements.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            vars.poweroff_reboot_flag = False


def ls_a_check(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    ach = "sh.xray"
    ach_meta = data["achievements"]["en"][ach]
    if find_re(pcmd, vars.ls_a_find_re, ach_meta) and pcmd[-1] == "0":
        do(data, ach, ach_meta, vars.ls_a_flag,vars)

    write_ach(data, vars.ls_a_flag,vars)


def shrc_check(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    ach = "sh.shrc"
    ach_meta = data["achievements"]["en"][ach]

    if find_re(pcmd, vars.shrc_find_re, ach_meta) and pcmd[-1] == "0":
        do(data, ach, ach_meta, vars.shrc_flag,vars)

    write_ach(data, vars.shrc_flag,vars)


def assassination_atmpt(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    ach = "sh.kill_try"
    ach_meta = data["achievements"]["en"][ach]

    if find_re(pcmd, vars.rm_rf_flag, ach_meta) and pcmd[-1] == "1":
        do(data, ach, ach_meta, vars.rm_rf_flag,vars)

    write_ach(data, vars.rm_rf_flag,vars)


def repeater(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    ach = "sh.repeater"
    ach_meta = data["achievements"]["en"][ach]

    if find_re(pcmd, vars.repeater_flag, ach_meta) and pcmd[-1] == "0":
        vars.repeater_times += 1

    if vars.repeater_times == 3:
        vars.repeater_times = 0
        do(data, ach, ach_meta, vars.repeater_flag,vars)

    write_ach(data, vars.repeater_flag,vars)


def vim_close(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    achs = ["vim.close.200", "vim.close.force"]
    for ach in achs:
        ach_meta = data["achievements"]["en"][ach]

        if pcmd[1] == "END" and find_re(pcmd, vars.vim_find_re, ach_meta):
            if ach == "vim.close.200" and pcmd[-1] == "0":
                do(data, ach, ach_meta, vars.vim_close_flag,vars)

            elif ach == "vim.close.force" and pcmd[-1] != "0":
                do(data, ach, ach_meta, vars.vim_close_flag,vars)

            write_ach(data, vars.vim_close_flag,vars)


def nano_close(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    achs = ["nano.close.200", "nano.close.force"]
    for ach in achs:
        ach_meta = data["achievements"]["en"][ach]

        if pcmd[1] == "END" and find_re(pcmd, vars.vim_find_re, ach_meta):
            if ach == "nano.close.200" and pcmd[-1] == "0":
                do(data, ach, ach_meta, vars.nano_close_flag,vars)

            elif ach == "nano.close.force" and pcmd[-1] != "0":
                do(data, ach, ach_meta, vars.nano_close_flag,vars)

            write_ach(data, vars.nano_close_flag,vars)

def nano_open(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    ach = "nano.open"
    ach_meta = data["achievements"]["en"][ach]
    if find_re(pcmd, vars.nano_find_re, ach_meta):
        do(data, ach, ach_meta, vars.nano_find_re,vars)

    write_ach(data, vars.nano_find_re,vars)

def vim_nano_exst(pcmd: list):
    with open("data/player data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    cmd = " ".join(str(arg) for arg in pcmd[2:]).strip()

    match = re.match(vars.vim_nano_exst_find_re, cmd)
    if match:
        # Вытравливаем только тот элемент, который не равен None
        path = next(item for item in match.groups() if item is not None).strip().replace('\\ ', ' ')

        full_path = os.path.expanduser(path)
        if not os.path.exists(full_path):
            ach = "vim_nano.new_exisiting_file"
            ach_meta = data["achievements"]["en"][ach]
            if find_re(pcmd, vars.vim_find_re, ach_meta):
                do(data, ach, ach_meta, vars.vim_nano_exst_flag,vars)

            write_ach(data, vars.vim_nano_exst_flag,vars)
            # TODO: Correct!


def do(dt, ach_idr, ach_mt, flag, vars_module):
    dt["achievements"][ach_idr]["done"] = True
    notifications.show_achievement(
        ach_mt["title"],
        ach_mt["description"]
    )
    if not getattr(vars_module, flag):
        setattr(vars_module, flag, True)

def write_ach(dt, flag, vars_module):
    if getattr(vars_module, flag):
        with open("data/player data.json", "w", encoding="utf-8") as f:
            json.dump(dt, f, ensure_ascii=False, indent=4)
        setattr(vars_module, flag, False)

def find_re(pcmd: list, RE, ach_mt):
    cmd = " ".join(str(arg) for arg in pcmd[2:]).strip()
    return re.search(RE, cmd, re.IGNORECASE) and not ach_mt["done"]


def parse():
    parse_list()
    vim_detector(vars.parsed)
    vim_time_achv(vars.vim_time_)
    poweroff_reboot_check(vars.parsed)
    ls_a_check(vars.parsed)
    shrc_check(vars.parsed)
    assassination_atmpt(vars.parsed)
    repeater(vars.parsed)
    vi_detector(vars.parsed)
    vim_close(vars.parsed)
