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



import time
import sys
import subprocess
import pathlib
import variables as vars
import os
import json
import signal
import re
import sys
import io
import pydoc
import textwrap
import install_conf




DAEMON_NAME = 'daemon.py'
daemon_path = pathlib.Path(__file__).resolve().parent / DAEMON_NAME
run = True

class Parser:
    daemon_flags_pattern = r"--(?:start|stop|status|logs|rm-logs|reboot)\b"
    daemon_pattern = r"\bdaemon\s+--(?:start|stop|status|logs|rm-logs|reboot)\b"
    ach_id_pattern = r"\b(ach)\s+(<[^>]+>)"
    ach_pattern = r'\bach\s+(?:--(?:locked|all|opened)|"\w+"|[^\s]+)'
    bash_pattern = r"^:!\s*(.*)"
    pipe_pattern = r"^(?!:!)([^|]+)\|(.*)"


    @staticmethod
    def parse_bash(log):
        bash_command = log.group(1)
        if bash_command:
            try:
                result = subprocess.run(
                    bash_command,
                    shell=True,
                    executable='/bin/bash',
                    #capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(result.stderr.strip())
            except Exception as e:
                #print(f"Happened an unexpected python-error: {e}")
                pass

    @staticmethod
    def parse_native_cmd(log):
        global run
        match log:

            case "h" | "help":
                print("""install-config - install a shell script for logging commands
ach --locked - print locked achievements
ach --all - print all achievements
ach --opened - print opened achievements
ach <ID> - print info about an achievement (angle brackets are expected!)
daemon --start - start the daemon
daemon --stop - stop the daemon 
daemon --reboot - reboot the daemon
daemon --status - print the daemon status
daemon --logs - print logs
daemon --rm-logs - delete logs
clear - clear the screen (could be non-working if you're running this script not from the system terminal)
use ':!' to use bash commands like in vim (pipes with utility-commands are supported)
q/quit - quit this program""")
            case "q" | "quit":
                run = False
            case "clear":
                subprocess.run(["clear"], stderr=subprocess.DEVNULL)
            case "install-config":
                install_conf.Installer.install_config()

            case _:
                Parser.parse(log)
    @staticmethod
    def parser(log):
        bash_match = re.match(Parser.bash_pattern, log)
        pipe_match = re.match(Parser.pipe_pattern, log)

        if bash_match:
            Parser.parse_bash(bash_match)
        elif pipe_match:
            Parser.parse_pipe(pipe_match)
        else:
            Parser.parse_native_cmd(log)

    @staticmethod
    def parse_pipe(log):
        if log:
            app_part = log.group(1).strip()
            bash_part = log.group(2).strip()
            captured_output = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured_output
            try:
                Parser.parser(app_part)
            finally:
                sys.stdout = old_stdout
            app_output_text = captured_output.getvalue()
            try:
                process = subprocess.Popen(
                    bash_part,
                    shell=True,
                    executable='/bin/bash',
                    stdin=subprocess.PIPE,
                    text=True
                )
                process.communicate(input=app_output_text)
            except Exception as e:
                print(f"{e}")

    @staticmethod
    def parse(log):
        achid_pat = None
        flags = {"--start", "--stop", "--status", "--logs", "--rm-logs", "--reboot"}
        string = " ".join(log.strip().split())

        daemon_pat = re.findall(Parser.daemon_pattern, string)
        ach_pat = re.findall(Parser.ach_pattern, string)
        try:
            achid_pat = list(re.findall(Parser.ach_id_pattern, string)[0])
            achid_pat = " ".join(achid_pat)
        except IndexError:
            pass

        daemon_pat = " ".join(daemon_pat)
        ach_pat = " ".join(ach_pat)

        if daemon_pat:
            tokens = daemon_pat.split()
        elif ach_pat:
            tokens = ach_pat.split()
        elif achid_pat:
            tokens = achid_pat.split()
        else:
            tokens = []

        try:
            if tokens[0] == "daemon" and len(tokens) > 1:
                flag = tokens[1].replace("--", "")
                flag = flag.replace("-", "")
                match flag:
                    case "start":
                        Daemon.start()
                    case "stop":
                        Daemon.stop()
                    case "status":
                        Daemon.status()
                    case "logs":
                        Daemon.logs()
                    case "rm_logs":
                        Daemon.rm_logs()
                    case "reboot":
                        Daemon.reboot()
                    case _:
                        print(f"Unknown flag: '{tokens[0]}'. Try again")
            elif tokens[0] == "ach" and len(tokens) > 1 and not achid_pat:

                flag = tokens[1].replace("--", "")
                match flag:
                    case "locked":
                        Ach.locked()
                    case "all":
                        Ach.all()
                    case "unlocked":
                        Ach.unlocked()
                    case _:
                        print(f"Unknown flag: '{tokens[0]}'. Try again")
            elif tokens[0] == "ach" and len(tokens) > 1 and achid_pat:
                flag = tokens[1].replace("<", "")
                flag = flag.replace(">", "")
                Ach.achid(flag)

            else:
                if log == "daemon":
                    print(f"""Possible actions with 'daemon':
daemon --start - start the daemon
daemon --stop - stop the daemon 
daemon --reboot - reboot the daemon
daemon --status - print the daemon status
daemon --logs - print logs
daemon --rm-logs - delete logs
""")
                elif log == "ach":
                    print(f"""Possible actions with 'ach':
ach --all - print all achievements
ach --opened - print opened achievements
ach <ID> - print info about an achievement
""")

                else:
                    print(f"Unknown command: '{log}'")

        except IndexError:
            if log == "daemon":
                print(f"""Possible actions with 'daemon':
daemon --start - start the daemon
daemon --stop - stop the daemon 
daemon --reboot - reboot the daemon
daemon --status - print the daemon status
daemon --logs - print logs
daemon --rm-logs - delete logs""")
            elif log == "ach":
                print(f"""Possible actions with 'ach':
ach --all - print all achievements
ach --opened - print opened achievements
ach <ID> - print info about an achievement""")

            else:
                print(f"Unknown command: '{log}'")

class Ach:
    @staticmethod
    def all():
        print("Printing the list of entire achievements...")
        with open("/home/george/Linux Achievements/data/achievements.json", "r", encoding='utf-8') as f:
            achs = json.load(f)

        with open("/home/george/Linux Achievements/data/player data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        achievements = achs["achievements"]["en"]

        for i in achievements:
            if not achievements[i]["secret"]:
                print(f"""Achievement: {achievements[i]["id"]}
Title: {achievements[i]["title"]} 
Description: {achievements[i]["description"]}
Difficulty: {achievements[i]["diff"]}
Done: {data["achievements"][i]["done"]}""")

    @staticmethod
    def locked():
        count_u=0
        count=0
        print("Printing the list of locked achievements...")
        with open("/home/george/Linux Achievements/data/achievements.json", "r", encoding='utf-8') as f:
            achs = json.load(f)

        with open("/home/george/Linux Achievements/data/player data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        achievements = achs["achievements"]["en"]

        for i in achievements:
            count+=1
            if not data["achievements"][i]["done"]:
                print(f"""Achievement: {achievements[i]["id"]}
Title: {achievements[i]["title"]}")
Description: {achievements[i]["description"]}
Difficulty: {achievements[i]["diff"]}""")
                count_u+=1

        print(f"Total locked: {count_u}/{count}")

    @staticmethod
    def unlocked():
        count_u = 0
        count = 0
        print("Printing the list of unlocked achievements...")
        with open("/home/george/Linux Achievements/data/achievements.json", "r", encoding='utf-8') as f:
            achs = json.load(f)

        with open("/home/george/Linux Achievements/data/player data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        achievements = achs["achievements"]["en"]

        for i in achievements:
            count+=1
            if data["achievements"][i]["done"]:
                print(f"""Achievement: {achievements[i]["id"]}
Title: {achievements[i]["title"]}")
Description: {achievements[i]["description"]}
Difficulty: {achievements[i]["diff"]}""")
                count_u+=1
        if count_u:
            print(f"Total unlocked: {count_u}/{count}")
            return
        print("It seems you have not unlocked any achievements yet")
    @staticmethod
    def achid(id):
        with open("/home/george/Linux Achievements/data/achievements.json", "r", encoding='utf-8') as f:
            achs = json.load(f)

        with open("/home/george/Linux Achievements/data/player data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        achievements = achs["achievements"]["en"]
        for i in achievements:
            if i == id:
                print(f"""Achievement: {achievements[i]["id"]}
Title: {achievements[i]["title"]}
Description: {achievements[i]["description"]}
Difficulty: {achievements[i]["diff"]}
Done: {data["achievements"][i]["done"]}
Secret: {achs["achievements"]["en"][i]["secret"]}""")
                return
        else:
            print(f"Cannot find the achievement: '{id}'")

class Daemon:
    DAEMON_NAME = 'daemon.py'
    daemon_path = pathlib.Path(__file__).resolve().parent / DAEMON_NAME
    @staticmethod
    def start():

        if os.path.exists('daemon.pid'):
            print("Unable to turn on the daemon. It's already running")

        else:
            print("Starting the daemon...")

            with open(vars.LOG_FILE_PATH, 'w', encoding='utf-8', buffering=1) as log_file:
                subprocess.Popen(
                    [sys.executable, str(daemon_path)],
                    start_new_session=True,  # Полностью отвязываем от текущей консоли
                    stdout=log_file,  # Все print() летят в файл
                    stderr=log_file  # Все ошибки летят в файл
                )
            print("[+] Daemon successfully started in background.")
    @staticmethod
    def stop():
        if not os.path.exists('daemon.pid'):
            print("Unable to turn off the daemon. It's already turned off")
        else:
            print("[-] Stopping the daemon...")

            # 1. Читаем PID процесса из файла
            with open('daemon.pid', 'r') as f:
                try:
                    pid = int(f.read().strip())
                except ValueError:
                    print("[!] PID file is corrupted. Cleaning up...")
                    os.remove('daemon.pid')
                    return

            try:
                # 2. Отправляем сигнал на завершение
                os.kill(pid, signal.SIGTERM)

                # 3. Ждем, пока процесс РЕАЛЬНО исчезнет из системы
                for _ in range(10):
                    try:
                        # Сигнал 0 не убивает процесс, но проверяет, жив ли он
                        os.kill(pid, 0)
                    except ProcessLookupError:
                        # Процесс успешно умер!
                        print("[+] Daemon successfully stopped.")
                        return
                    time.sleep(0.5)  # Проверяем каждые полсекунды (так быстрее)
                else:
                    print("[!] Daemon is taking too long to stop. Sending SIGKILL...")
                    try:
                        os.kill(pid, signal.SIGKILL)
                        print("[+] Daemon killed forcefully.")
                    except ProcessLookupError:
                        pass

            except ProcessLookupError:
                print("[-] Process not found in system. Cleaning up frozen PID file...")

            # 4. В любом случае удаляем PID-файл, так как процесса больше нет
            if os.path.exists('daemon.pid'):
                os.remove('daemon.pid')
    @staticmethod
    def status():
        if not os.path.exists('daemon.pid'):
            print("[•] Status: STOPPED (PID file does not exist)")

        else:
            # 2. Читаем PID из файла
            with open('daemon.pid', 'r') as f:
                pid = int(f.read().strip())

            try:
                # 3. Linux-магия: отправка сигнала '0' процессу.
                # Это не убивает процесс, а просто проверяет, жив ли он в системе.
                os.kill(pid, 0)
                print(f"[•] Status: RUNNING (PID: {pid})")

            except (ProcessLookupError, ValueError):
                # 4. Если вылетит эта ошибка, значит PID в системе больше нет (демон упал!)
                print(
                    "[•] Status: CRASHED / DEAD (PID file exists, but process is not running)")

                # Дополнительно: можно сразу удалить мусорный файл
                try:
                    os.remove('daemon.pid')
                    print("[+] Cleaned up dead PID file.")
                except OSError:
                    pass
    @staticmethod
    def reboot():
        if not os.path.exists('daemon.pid'):
            print("Unable to reboot the daemon. It's not running")

        else:
            print("Rebooting the daemon...")

            with open('daemon.pid', 'r') as f:
                try:
                    pid = int(f.read().strip())
                except ValueError:
                    os.remove('daemon.pid')
                    return
            os.kill(pid, signal.SIGTERM)

            print("[-] Turrning the daemon off...")
            for _ in range(10):

                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    print("[+] The daemon successfully killed...")

                time.sleep(0.5)

            else:
                print("[!] Daemon is taking too long to stop. Sending SIGKILL...")
                try:
                    os.kill(pid, signal.SIGKILL)
                    print("[+] Daemon killed forcefully.")
                except ProcessLookupError:
                    pass

            print("[+] Starting the daemon...")
            with open(vars.LOG_FILE_PATH, 'w', encoding='utf-8', buffering=1) as log_file:
                subprocess.Popen(
                    [sys.executable, str(daemon_path)],
                    start_new_session=True,
                    stdout=log_file,
                    stderr=log_file
                )
            print("[+] Daemon successfully rebooted and started in background.")
    @staticmethod
    def rm_logs():
        with open("/home/george/Linux Achievements/code/daemon.log", "w", encoding='utf-8') as logs:
            logs.write("")

        print("Successfully cleared the log file")
    @staticmethod
    def logs():
        if os.path.getsize("/home/george/Linux Achievements/code/daemon.log") == 0:
            print("The file is empty")
            return
        with open("/home/george/Linux Achievements/code/daemon.log", "r", encoding='utf-8') as f:
            logs = f.readlines()

        for i in logs:
            print(i.strip())


def main():
    global run
    if "TERM" not in os.environ or not os.environ["TERM"]:
        os.environ["TERM"] = "xterm-256color"

    print("""
    ###           ###    ###    ###    ###    ###   ###    ###         ####         ######      ###    ###   ###    #########    ###    ###    #########    ###      ###    #########   ###    ###  #########    ########
    ###           ###    ###    ###    ###    ###    ###  ###         ######      ##########    ###    ###   ###    #########    ###    ###    #########    ####     ###    #########   ###    ###  #########   ##########
    ###           ###    #####  ###    ###    ###     ######         ###  ###     ###    ###    ###    ###   ###    ###          ###    ###    ###          ############    ###         #####  ###     ###      ###
    ###           ###    ##########    ###    ###      ####         ##########    ###           ##########   ###    #########     ###  ###     #########    ###  ##  ###    #########   ##########     ###       #########
    ###           ###    ###  #####    ###    ###     ######        ##########    ###     ##    ##########   ###    #########      ######      #########    ###      ###    ###         ###  #####     ###        ########
    ###           ###    ###    ###    ###    ###    ###  ###       ###    ###    ###     ##    ###    ###   ###    ###             ####       ###          ###      ###    ###         ###    ###     ###      #      ###
    ##########    ###    ###    ###     ########    ###    ###      ###    ###    ##########    ###    ###   ###    #########       ####       #########    ###      ###    #########   ###    ###     ###     ####   ####
    ##########    ###    ###    ###      ######     ###    ###      ###    ###      ######      ###    ###   ###    #########        ##        #########    ###      ###    #########   ###    ###     ###      #########
    """)
    print('''Welcome to Linux Achievements! Linux Achievements is a fully open-source software, adding achievements into your GNU/Linux system and licensed under AGPLv3. 
Check my github: https://github.com/SIBDuck
Here you can check your achievements and track your progress.
Type <h> or <help> for help, type <install-config> to install a shell script for logging commands''')

    DAEMON_NAME = 'daemon.py'
    daemon_path = pathlib.Path(__file__).resolve().parent / DAEMON_NAME

    while run:
        try:
            time.sleep(0.01)
            inp = input("> ")

            Parser.parser(inp)

        except KeyboardInterrupt:
            break
    print("\nGoodbye...")

if __name__ == "__main__":
    main()