import json

def load_json(file_path, default):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)