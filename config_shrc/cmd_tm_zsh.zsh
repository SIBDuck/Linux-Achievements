#!/bin/zsh

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


# Флаг состояния (0 - свободен, 1 - редактор запущен)
typeset -g _ACH_EDITOR_ACTIVE=0

# Путь к изолированной RAM текущего пользователя
typeset -g _ACH_RAM_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/linux-achievements"

# Инициализация: создаем RAM-директорию и записываем дефолтный редактор
if mkdir -p "$_ACH_RAM_DIR" 2>/dev/null; then
    _ed="${EDITOR:-nano}"
    _ed="${_ed%% *}"   # Убираем аргументы
    _ed="${_ed##*/}"   # Убираем путь к бинарнику
    print -r -- "$_ed" > "$_ACH_RAM_DIR/editor"
    touch "$_ACH_RAM_DIR/daemon.log"
fi


# Функция-помощник: циклично убирает sudo и раскрывает алиасы в Zsh
_resolve_alias() {
    local cmd="$1"
    local first_word

    while true; do
        if [[ "$cmd" == "sudo "* ]]; then
            cmd="${cmd#sudo }"
        elif [[ "$cmd" == -* ]]; then
            cmd="${cmd#* }"
        else
            break
        fi
    done

    first_word="${cmd%% *}"

    # В Zsh проверка алиаса делается через алиасы или глобальные алиасы
    if [[ -n "${aliases[$first_word]}" ]]; then
        local alias_body="${aliases[$first_word]}"
        print -r -- "${alias_body}${cmd#$first_word}"
    else
        print -r -- "$cmd"
    fi
}


# Хук 1: Срабатывает ДО запуска команды (preexec)
_log_achievements_start() {
    local 1="$1" # Полная строка введенной команды

    [[ -z "$1" || "$1" == *"_log_achievements"* ]] && return
    (( _ACH_EDITOR_ACTIVE == 1 )) && return

    local resolved_cmd=$(_resolve_alias "$1")
    local first_word="${resolved_cmd%% *}"

    case "$first_word" in
        vi|vim|nvim|nano|emacs|mcedit|gedit|kate|micro|visudo|sudoedit)
            _ACH_EDITOR_ACTIVE=1
            mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
            strftime -s _timestamp "%s"
            print -r -- "$_timestamp START $1" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
            ;;
        *)
            ;;
    esac
}


# Хук 2: Срабатывает ПОСЛЕ завершения команды (precmd)
_log_achievements_bash() {
    local exit_code=$?

    # Если редактор был активен, а мы попали в precmd, значит редактор завершился
    if (( _ACH_EDITOR_ACTIVE == 1 )); then
        _ACH_EDITOR_ACTIVE=0

        # Читаем последнюю команду из истории Zsh
        local last_cmd="${history[$((HISTCMD-1))]}"
        [[ -z "$last_cmd" ]] && last_cmd="unknown_editor_cmd"

        last_cmd=$(_resolve_alias "$last_cmd")

        mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
        strftime -s _timestamp "%s"
        print -r -- "$_timestamp END $last_cmd $exit_code" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
    fi
}


# Хук 3: Срабатывает при выходе из оболочки / закрытии терминала
_log_achievements_exit() {
    if (( _ACH_EDITOR_ACTIVE == 1 )); then
        mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
        strftime -s _timestamp "%s"
        print -r -- "$_timestamp END active_editor_terminated 129" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
        _ACH_EDITOR_ACTIVE=0
    fi
}


# Регистрация хуков в Zsh
autoload -Uz add-zsh-hook
add-zsh-hook preexec _log_achievements_start
add-zsh-hook precmd _log_achievements_bash
add-zsh-hook zshexit _log_achievements_exit