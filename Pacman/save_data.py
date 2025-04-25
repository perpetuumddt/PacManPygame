import json
import os

SAVE_FILE = "save.json"

def load_progress():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {"unlocked_level": 1}

def save_progress(unlocked_level):
    current = load_progress()
    if unlocked_level > current["unlocked_level"]:
        with open(SAVE_FILE, "w") as f:
            json.dump({"unlocked_level": unlocked_level}, f)
