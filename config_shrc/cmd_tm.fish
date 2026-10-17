# Copyright (C) 2026 SIBDuck
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# ==============================================================================
# WARNING & SECURITY NOTICE:
# - This script logs the last terminal command
# - Use strictly at your own risk. The author assumes no liability for leaks.
#==============================================================================

# Сохраняем состояние в глобальной переменной
set -g _ACH_EDITOR_ACTIVE 0
set -g _ACH_RAM_DIR "$XDG_RUNTIME_DIR/linux-achievements"
if test -z "$XDG_RUNTIME_DIR"
    set _ACH_RAM_DIR "/run/user/(id -u)/linux-achievements"
end

# Инициализация RAM-директории
if mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
    set -l _ed "$EDITOR"
    if test -z "$_ed"
        set _ed "nano"
    end
    set _ed (string split ' ' $_ed)[1]
    set _ed (basename "$_ed")
    echo "$_ed" > "$_ACH_RAM_DIR/editor"
    touch "$_ACH_RAM_DIR/daemon.log"
end


# Помощник для очистки sudo и аргументов
function _resolve_alias
    set -l cmd $argv[1]
    while true
        if string match -q "sudo *" -- $cmd
            set cmd (string replace -r "^sudo " "" -- $cmd)
        else if string match -q "-*" -- $cmd
            set cmd (string replace -r "^[^ ]+ " "" -- $cmd)
        else
            break
        end
    end
    echo $cmd
end


# Срабатывает ДО запуска команды
function _log_achievements_start --on-event fish_preexec
    if test $_ACH_EDITOR_ACTIVE -eq 1
        return
    end

    set -l full_cmd $argv[1]
    if string match -q "*_log_achievements*" -- $full_cmd
        return
    end

    set -l resolved (_resolve_alias "$full_cmd")
    set -l first_word (string split ' ' -- $resolved)[1]

    switch $first_word
        case vi vim nvim nano emacs mcedit gedit kate micro visudo sudoedit
            set -g _ACH_EDITOR_ACTIVE 1
            mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
            date +%s > "$_ACH_RAM_DIR/tmp_time"
            set -l timestamp (cat "$_ACH_RAM_DIR/tmp_time")
            rm -f "$_ACH_RAM_DIR/tmp_time"
            echo "$timestamp START $full_cmd" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
    end
end


# Срабатывает ПОСЛЕ выполнения команды
function _log_achievements_post --on-event fish_postexec
    set -l exit_code $status

    if test $_ACH_EDITOR_ACTIVE -eq 1
        set -g _ACH_EDITOR_ACTIVE 0

        # Получаем последнюю команду из истории Fish
        set -l last_cmd (history max 1)
        if test -z "$last_cmd"
            set last_cmd "unknown_editor_cmd"
        end

        set last_cmd (_resolve_alias "$last_cmd")

        mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
        date +%s > "$_ACH_RAM_DIR/tmp_time"
        set -l timestamp (cat "$_ACH_RAM_DIR/tmp_time")
        rm -f "$_ACH_RAM_DIR/tmp_time"
        echo "$timestamp END $last_cmd $exit_code" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
    end
end


# Срабатывает при выходе из сессии Fish
function _log_achievements_exit --on-event fish_exit
    if test $_ACH_EDITOR_ACTIVE -eq 1
        mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
        date +%s > "$_ACH_RAM_DIR/tmp_time"
        set -l timestamp (cat "$_ACH_RAM_DIR/tmp_time")
        rm -f "$_ACH_RAM_DIR/tmp_time"
        echo "$timestamp END active_editor_terminated 129" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
        set -g _ACH_EDITOR_ACTIVE 0
    end
end