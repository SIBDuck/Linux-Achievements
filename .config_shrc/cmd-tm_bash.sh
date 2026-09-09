#!/bin/bash

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
_ACH_EDITOR_ACTIVE=0

# Путь к изолированной RAM текущего пользователя
_ACH_RAM_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/linux-achievements"


# Функция-помощник: циклично убирает любое количество sudo и раскрывает алиасы
_resolve_alias() {
    local cmd="$1"

    # Цикл крутится, пока команда начинается с "sudo" или флага "-"
    while true; do
        if [[ "$cmd" == "sudo "* ]]; then
            cmd="${cmd#sudo }" # Срезаем "sudo "
        elif [[ "$cmd" == -* ]]; then
            cmd="${cmd#* }"    # Срезаем флаги (например, "-E" или "-u root")
        else
            break # Если больше префиксов нет, выходим из цикла
        fi
    done

    # Извлекаем очищенное первое слово
    local first_word=$(echo "$cmd" | awk '{print $1}')

    # Раскрываем алиас, если он существует
    if alias "$first_word" &>/dev/null; then
        local alias_body=$(alias "$first_word" | sed "s/^alias [^=]*='\(.*\)'/\1/")
        echo "${alias_body}${cmd#$first_word}"
    else
        echo "$cmd"
    fi
}


# Функция 1: Срабатывает ДО запуска команды (Фиксируем СТАРТ только для редакторов)
_log_achievements_start() {
    [[ -z "$BASH_COMMAND" || "$BASH_COMMAND" == "$PROMPT_COMMAND" ]] && return
    [[ "$BASH_COMMAND" == *"_log_achievements"* || "$BASH_COMMAND" == *"__vte"* ]] && return
    (( _ACH_EDITOR_ACTIVE == 1 )) && return

    # Теперь resolved_cmd вернет "vim ...", даже если было "sudo vim" или "sudo v"
    local resolved_cmd=$(_resolve_alias "$BASH_COMMAND")
    local first_word=$(echo "$resolved_cmd" | awk '{print $1}')

    case "$first_word" in
        vi|vim|nvim|nano|emacs|mcedit|gedit|kate|micro|visudo|sudoedit)
            _ACH_EDITOR_ACTIVE=1
            mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
            printf "%(%s)T START %s\n" "-1" "$BASH_COMMAND" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
            ;;
        *)
            return
            ;;
    esac
}


# Инициализация: создаем RAM-директорию и записываем дефолтный редактор (оптимизировано)
if mkdir -p "$_ACH_RAM_DIR" 2>/dev/null; then
    _ed="${EDITOR:-nano}"
    _ed="${_ed%% *}"   # Убираем аргументы (например, "vim -u NONE" -> "vim")
    _ed="${_ed##*/}"   # Убираем путь к бинарнику (например, "/usr/bin/nano" -> "nano")
    printf "%s\n" "$_ed" > "$_ACH_RAM_DIR/editor"
    touch "$_ACH_RAM_DIR/daemon.log"
fi


# Функция 2: Срабатывает ПОСЛЕ завершения команды (Фиксируем ИСХОД для всего)
_log_achievements_bash() {
    local exit_code=$?
    [[ "$BASH_COMMAND" == "$PROMPT_COMMAND" ]] && return

    history -a
    local last_cmd=$(history 1 | sed 's/^[ ]*[0-9]*[ ]*//')
    [[ -z "$last_cmd" || "$last_cmd" == *"_log_achievements"* || "$last_cmd" == *"__vte"* ]] && return

    #######
    last_cmd=$(_resolve_alias "$last_cmd")
    #######

    _ACH_EDITOR_ACTIVE=0

    mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
    printf "%(%s)T END %s %s\n" "-1" "$last_cmd" "$exit_code" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
}


# Функция 3: Срабатывает БРУТАЛЬНО при закрытии терминала крестиком
_log_achievements_exit() {
    trap - DEBUG

    local resolved_cmd=$(_resolve_alias "$BASH_COMMAND")
    local first_word=$(echo "$resolved_cmd" | awk '{print $1}')

    case "$first_word" in
        vi|vim|nvim|nano|emacs|mcedit|gedit|kate|micro)
            (( _ACH_EDITOR_ACTIVE == 0 )) && return
            ;;
        *)
            return
            ;;
    esac

    mkdir -p "$_ACH_RAM_DIR" 2>/dev/null
    printf "%(%s)T END %s 129\n" "-1" "$BASH_COMMAND" > "$_ACH_RAM_DIR/last_cmd" 2>/dev/null
    _ACH_EDITOR_ACTIVE=0
}


# Отключаем трассировку функций для ловушек
set +t

# Внедряем хук на финиш команды
if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_log_achievements_bash"
elif [[ "$PROMPT_COMMAND" != *"_log_achievements_bash"* ]]; then
    PROMPT_COMMAND="_log_achievements_bash; $PROMPT_COMMAND"
fi

# Активируем ловушки
trap '_log_achievements_start' DEBUG
trap '_log_achievements_exit' EXIT

export PATH="$HOME/.local/bin:$PATH"
