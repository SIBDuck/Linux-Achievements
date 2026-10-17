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
# CLI utility to control the daemon and player's progress

import time
import subprocess
import pathlib
import os
import signal
import re
import sys
import io
import json
import cmd_parser

# Getting paths
ach_path, data_path = cmd_parser.Parser.paths()

running = True
import install_conf
import variables as v


class Parser:
    # Regular expressions to parse strings from the utility
    # RE to find commands linked with daemon
    daemon_pattern = r"\bdaemon\s+--(?:start|stop|status|logs|rm-logs|reboot|last-cmd)\b"
    # REs to find commands linked with achievements
    # RE to find command `ach <ID>`
    ach_id_pattern = r"\b(ach)\s+(<[^>]+>)"
    # RE to find commands linked with showing achievements (`ach <ID> not included`)
    ach_pattern = r'\bach\s+(?:--(?:locked|all|opened)|"\w+"|[^\s]+)'
    # REs to parse bash commands (`:!`) and pipes respectively
    bash_pattern = r"^:!\s*(.*)"
    pipe_pattern = r"^(?!:!)([^|]+)\|(.*)"

    # Function to parse bash commands (`:!`)
    @staticmethod
    def parse_bash(log):
        # Getting the command (on position 1 in a parsed string)
        bash_command = log.group(1)
        if bash_command:
            try:
                # Executing
                result = subprocess.run(
                    bash_command,
                    shell=True,
                    executable='/bin/bash',
                    text=True
                )
                # Printing an error if it is necessary
                if result.returncode != 0:
                    print(result.stderr.strip())
            except Exception as e:
                print(f"Unexpected error occured: {e}")

    @staticmethod
    def configs_installed():
        # Get player's data
        with open(v.DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Get shell data
        shell_data = data["configs_installed"]
        # Print info about installed configs
        for shell in shell_data:
            if shell_data[shell]:
                print(shell)
        else:
            print("No configs installed. You can install one using `install-config`")

    # Function to print info about configs
    @staticmethod
    def configs_all():
        # Get player's data
        with open(v.DATA_PATH, "r", encoding='utf-8') as f:
            data = json.load(f)
        # Get shell data
        shell_data = data["configs_installed"]
        # Print info about every shell
        for shell in shell_data:
            print(f"Shell: {shell}. Installed: {shell_data[shell]}")  # configs[i] = True | False

    # Function to parse native utility commands
    @staticmethod
    def parse_native_cmd(log):
        global running
        # Parsing a command
        match log:
            case "h" | "help":
                print("""'install-config' - install a shell script for logging commands
'configs-installed' - print info about installed configs for the shells
'configs-all' - print info about shells and configs for them
'ach --locked' - print locked achievements
'ach --all' - print all achievements
'ach --opened' - print opened achievements
'ach <ID>' - print info about an achievement (angle brackets are expected!)
'daemon --start' - start the daemon
'daemon --stop' - stop the daemon 
'daemon --reboot' - reboot the daemon
'daemon --status' - print the daemon status
'daemon --logs' - print logs
'daemon --rm-logs' - delete logs
'clear' - clear the screen (could be non-working if you're running this script not from the system terminal)
'fetch' - print the welcome screen
use ':!' to use bash commands like in vim (pipes with utility-commands are supported)
'q'/'quit' - quit this program""")
            case "q" | "quit":
                running = False
            case "clear":
                subprocess.run(["clear"], stderr=subprocess.DEVNULL)
            case "install-config":
                install_conf.Installer.install_config()
            case "configs-all":
                Parser.configs_all()
            case "installed-configs":
                Parser.configs_installed()
            # Welcome screen
            case "fetch":
                print("""
    ###           ###    ###    ###    ###    ###   ###    ###         ####         ######      ###    ###   ###    #########    ###    ###    #########    ###      ###    #########   ###    ###  #########    ########
    ###           ###    ###    ###    ###    ###    ###  ###         ######      ##########    ###    ###   ###    #########    ###    ###    #########    ####     ###    #########   ###    ###  #########   ##########
    ###           ###    #####  ###    ###    ###     ######         ###  ###     ###    ###    ###    ###   ###    ###          ###    ###    ###          ############    ###         #####  ###     ###      ###
    ###           ###    ##########    ###    ###      ####         ##########    ###           ##########   ###    #########     ###  ###     #########    ###  ##  ###    #########   ##########     ###       #########
    ###           ###    ###  #####    ###    ###     ######        ##########    ###     ##    ##########   ###    #########      ######      #########    ###      ###    ###         ###  #####     ###        ########                ###           ###    ###    ###    ###    ###    ###  ###       ###    ###    ###     ##    ###    ###   ###    ###             ####       ###          ###      ###    ###         ###    ###     ###      #      ###
    ##########    ###    ###    ###     ########    ###    ###      ###    ###    ##########    ###    ###   ###    #########       ####       #########    ###      ###    #########   ###    ###     ###     ####   ####
    ##########    ###    ###    ###      ######     ###    ###      ###    ###      ######      ###    ###   ###    #########        ##        #########    ###      ###    #########   ###    ###     ###      #########
                """)
                print('''Welcome to Linux Achievements! Linux Achievements is a fully open-source (free) software, \
adding achievements into your GNU/Linux system and licensed funder AGPLv3 or later. 
Check my github: https://github.com/SIBDuck
Here you can check your achievements and track your progress.
Type <h> or <help> for help, type <install-config> to install a shell script for logging commands''')
            case _:
                Parser.parse(log)

    # Main function to parse commands typing in the utility terminal
    @staticmethod
    def main_parse(log):
        # Find bash commands and pipes respectively
        bash_match = re.match(Parser.bash_pattern, log)
        pipe_match = re.match(Parser.pipe_pattern, log)
        if log == '':
            return

        # Parse bash, pipes and native commands respectively
        if bash_match:
            Parser.parse_bash(bash_match)
        elif pipe_match:
            Parser.parse_pipe(pipe_match)
        else:
            Parser.parse_native_cmd(log)

    # Function to parse pipes
    @staticmethod
    def parse_pipe(log):
        if log:
            # Find native command part
            app_part = log.group(1).strip()
            # Find bash command after pipe part
            bash_part = log.group(2).strip()
            # Intercept the standard output stream  to RAM buffer to transfer the first command output to bash pipe
            captured_output = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured_output

            try:
                # Parse native part
                Parser.main_parse(app_part)
            finally:
                # Restore the standard output stream back to the system terminal
                sys.stdout = old_stdout
            # Extract the captured text from the RAM buffer to feed it into the Bash pipe
            app_output_text = captured_output.getvalue()
            try:
                # Execute the target Bash command with redirected standard input (stdin)
                process = subprocess.Popen(
                    bash_part,
                    shell=True,
                    executable='/bin/bash',
                    stdin=subprocess.PIPE,
                    text=True
                )
                # Feed the captured output string into the running Bash process via pipe
                process.communicate(input=app_output_text)
            except Exception as e:
                print("During parsing pipes an error occurred:")
                print(f"{e}")

    # Function to parse Daemon and achievement linked commands
    @staticmethod
    def parse(log):
        achid_pat = None
        flags = {"--start", "--stop", "--status", "--logs", "--rm-logs", "--reboot"}
        # Normalize the input string by trimming edges and compressing multiple spaces into a single space
        string = " ".join(log.strip().split())
        # Find daemon linked and achievement linked commands respectively
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
                flag = flag.replace("-", "_")
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
                    case "last_cmd":
                        Daemon.last_cmd()
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

                        print(f"Unknown flag: '{tokens[1]}'. Try again")
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
ach --locked - print locked achievements
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
        with open(ach_path, "r", encoding='utf-8') as f:
            achs = json.load(f)

        with open(data_path, 'r', encoding='utf-8') as f:
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
        count_u = 0
        count = 0
        print("Printing the list of locked achievements...")
        with open(ach_path, "r", encoding='utf-8') as f:
            achs = json.load(f)

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        achievements = achs

        for i in achievements:
            count += 1
            if not data["achievements"][i]["done"]:
                print(f"""Achievement: {achievements[i]["id"]}
Title: {achievements[i]["title"]}")
Description: {achievements[i]["description"]}
Difficulty: {achievements[i]["diff"]}""")
                count_u += 1

        print(f"Total locked: {count_u}/{count}")

    @staticmethod
    def unlocked():
        count_u = 0
        count = 0
        print("Printing the list of unlocked achievements...")
        with open(ach_path, "r", encoding='utf-8') as f:
            achs = json.load(f)

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        achievements = achs["achievements"]["en"]

        for i in achievements:
            count += 1
            if data["achievements"][i]["done"]:
                print(f"""Achievement: {achievements[i]["id"]}
Title: {achievements[i]["title"]}")
Description: {achievements[i]["description"]}
Difficulty: {achievements[i]["diff"]}""")
                count_u += 1
        if count_u:
            print(f"Total unlocked: {count_u}/{count}")
            return
        print("It seems you have not unlocked any achievements yet")

    @staticmethod
    def achid(id):
        with open(ach_path, "r", encoding='utf-8') as f:
            achs = json.load(f)

        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        achievements = achs
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
    def get_pid():
        with open(v.DAEMON_PID_PATH, "r", encoding="utf-8") as pids:
            try:
                pid = int(pids.read().strip())
                return pid

            except ValueError:
                print(
                    "PID file was corrupted... Cleaning up. Find and kill the daemon on your own if it's still running")
                if os.path.exists(v.DAEMON_PID_PATH):
                    os.remove(v.DAEMON_PID_PATH)
                return None

    @staticmethod
    def start(reboot=False):
        if os.path.exists(v.DAEMON_PID_PATH):
            pid = Daemon.get_pid()
            if pid is None:
                print("Unable to get PID.")
                return
        else:
            daemon_binary_path = pathlib.Path.home() / ".local" / "bin" / v.DAEMON_NAME
            try:
                with open(os.devnull, 'r') as devnull_in, \
                        open(v.LOG_FILE_PATH, 'w', encoding='utf-8', buffering=1) as log_out:
                    subprocess.Popen(
                        [str(daemon_binary_path)],
                        stdin=devnull_in,
                        stdout=log_out,
                        stderr=log_out,
                        start_new_session=True
                    )
                if not reboot:
                    print("[+] Daemon successfully started in background.")
                else:
                    print("[+] Daemon successfully rebooted and started in background.")
            except FileNotFoundError:
                print(f"[!] Error: Binary file not found at {daemon_binary_path}")
                print("Make sure you compiled 'daemon.py' and moved it to ~/.local/bin/")
            except Exception as e:
                if not reboot:
                    print(f"[!] Unexpected error starting daemon: {e}")
                else:
                    print(f"[!] Unexpected error rebooting daemon: {e}")

    @staticmethod
    def stop():
        info = dict()
        if os.path.exists(v.DAEMON_PID_PATH):
            pid = Daemon.get_pid()
            if pid is None:
                print("Unable to get PID.")
                return
            try:
                with open(f"/proc/{pid}/status", "r", encoding="utf-8") as prc:
                    for line in prc:
                        if line.startswith(("Name:", "Pid:")):
                            key, value = line.split(":", 1)
                            key = key.lower()
                            info[key.strip()] = value.strip()
                if info:
                    if info['name'] == v.DAEMON_NAME and info['pid']:
                        try:
                            os.kill(pid, signal.SIGTERM)
                            for _ in range(10):
                                try:
                                    os.kill(pid, 0)
                                except ProcessLookupError:
                                    print("[+] Daemon successfully stopped.")
                                    break
                                time.sleep(0.5)
                            else:
                                print("[!] Daemon is taking too long to stop. Killing it forcibly...")
                                try:
                                    os.kill(pid, signal.SIGKILL)
                                    print("[+] Daemon killed forcefully.")
                                except ProcessLookupError:
                                    pass
                        except ProcessLookupError:
                            print("[-] Process not found in system.")
                        if os.path.exists(v.DAEMON_PID_PATH):
                            print("Cleaning up frozen PID file...")
                            os.remove(v.DAEMON_PID_PATH)
                            return
                    else:
                        print("The process exists, but it's not the daemon.")

            except FileNotFoundError:

                print("[+] Daemon successfully stopped.")
                if os.path.exists(v.DAEMON_PID_PATH):
                    os.remove(v.DAEMON_PID_PATH)
                return
        else:
            print("PID file does not exist (Daemon is already stopped or the file was killed forcibly)")

    @staticmethod
    def last_cmd():
        with open(v.PATH_LCMD, "r", encoding="utf-8") as log_file:
            logs = log_file.read().strip()
        print(logs)

    @staticmethod
    def status():
        if not os.path.exists(v.DAEMON_PID_PATH):
            print("[•] Status: STOPPED (PID file does not exist)")

        else:
            with open(v.DAEMON_PID_PATH, 'r') as f:
                pid = int(f.read().strip())

            try:
                os.kill(pid, 0)
                print(f"[•] Status: RUNNING (PID: {pid})")

            except (ProcessLookupError, ValueError):
                print(
                    "[•] Status: CRASHED / DEAD (PID file exists, but process is not running)")

                try:
                    os.remove('daemon.pid')
                    print("[+] Cleaned up dead PID file.")
                except OSError:
                    pass

    @staticmethod
    def reboot():
        Daemon.stop()
        Daemon.start(reboot=True)

    @staticmethod
    def rm_logs():
        with open(v.LOG_FILE_PATH, "w", encoding='utf-8') as logs:
            logs.write("")

        print("Successfully cleared the log file")

    @staticmethod
    def logs():
        try:
            if os.path.getsize(v.LOG_FILE_PATH) == 0:
                print("The file is empty")
                return
        except FileNotFoundError:
            # Touch the file if it does not exist
            pathlib.Path(v.LOG_FILE_PATH).touch()
            print("The file did not exist, but has been touched")
        with open(v.LOG_FILE_PATH, "r", encoding='utf-8') as f:
            logs = f.readlines()

        for i in logs:
            print(i.strip())


def main():
    global running
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
    print('''Welcome to Linux Achievements! Linux Achievements is a fully open-source (free) software, \
adding achievements into your GNU/Linux system and licensed under AGPLv3. 
Check my github: https://github.com/SIBDuck
Here you can check your achievements and track your progress.
Type <h> or <help> for help, type <install-config> to install a shell script for logging commands''')

    while running:
        try:
            time.sleep(0.01)
            inp = input("> ")

            Parser.main_parse(inp)

        except KeyboardInterrupt:
            break
    print("\nGoodbye...")


if __name__ == "__main__":
    main()
