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



import os

def os_join(path):
    return os.path.expanduser(path)

def add_to_path(shell):
    print(f"Installing config for {shell}...")
    match shell:
        case "bash" | "zsh":


            target_file = os_join(f"~/.{shell}rc")

            line_to_add = 'export PATH="$HOME/.local/bin:$PATH"\n'

            if not os.path.exists(target_file):
                with open(target_file, "w", encoding='utf-8') as f:
                    pass
            with open(target_file, "r", encoding='utf-8') as f:
                content = f.read()

            if 'export PATH="$HOME/.local/bin:$PATH"' not in content:
                with open(target_file, "a", encoding='utf-8') as f:
                    if content and not content.endswith("\n"):
                        f.write("\n")
                    f.write(line_to_add)
        case "fish":

            config_dir = os.path.expanduser("~/.config/fish")
            target_file = os.path.join(config_dir, "config.fish")
            line_to_add = "fish_add_path ~/.local/bin\n"

            os.makedirs(config_dir, exist_ok=True)

            if not os.path.exists(target_file):
                with open(target_file, 'w', encoding='utf-8') as f:
                    pass

            with open(target_file, "r", encoding='utf-8') as f:
                content = f.read()

            if "fish_add_path ~/.local/bin" not in content:
                with open(target_file, 'a', encoding='utf-8') as f:
                    if content and not content.endswith("\n"):
                        f.write("\n")
                    f.write(line_to_add)

    print(f"Successfully installed the config for your shell: {shell}")
