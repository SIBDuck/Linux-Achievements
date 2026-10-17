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
import hashlib
def calculate_hash(data_dict):
    SALT_1 = "ThisIsASuperSecretSalt1"
    clean_data = {k: v for k, v in data_dict.items() if k != "file_hash"}
    data_string = json.dumps(clean_data, sort_keys=True) + SALT_1
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()