import json
import hashlib
def calculate_hash(data_dict):
    SALT_1 = "ThisIsASuperSecretSalt1"
    clean_data = {k: v for k, v in data_dict.items() if k != "file_hash"}
    data_string = json.dumps(clean_data, sort_keys=True) + SALT_1
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()