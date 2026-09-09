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
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.dirname(current_dir)

hidden_dir = os.path.join(project_root, ".config_shrc")

sys.path.append(hidden_dir)

import installer_shell # The error could be ignored


class Installer:
    @staticmethod
    def install_config_shell(shell):
        installer_shell.add_to_path(shell)


        return
    @staticmethod
    def install_config():
        print("""This script installs the shell script for logging commands""")
        print("""Type <q> or <quit> to quit""")
        while True:
            try:
                time.sleep(0.01)
                inp = input("Which shell would you like to install the config for (bash, zsh, fish, q or quit to quit)? (install-config)> ")
                match inp:
                    case "quit" | "q":
                        print("\nQuiting installing mode...")
                        return
                    case "bash" | "zsh" | "fish" as shell:
                        print(f"Are you sure you want to install the config for {shell}? [Y/n]")
                        inp1 = input("(install-config)> ")
                        match inp1:
                            case "" | "Y" | "y":
                                Installer.install_config_shell(shell)
                                print("\nQuiting installing mode...")

                                return
                            case "n":
                                continue
                            case unknown_status:
                                print(f"Unknown action: '{unknown_status}'")
                    case unknown_status:
                        print(f"Unknown action: '{unknown_status}'")
            except KeyboardInterrupt:
                print("\nQuiting installing mode...")
                return

