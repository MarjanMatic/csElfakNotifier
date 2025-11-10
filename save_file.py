import json
import time
import os

SAVE_FILENAME = "last_check.json"

def create_save_object():
    return {
        "timestamp": int(time.time()),
        "courses": {}
    }

def get(course_ids) -> tuple[bool, dict]:
    if os.path.isfile(SAVE_FILENAME) == False:
        save_object = _create_file(course_ids)
        return save_object, True
    else:
        with open(SAVE_FILENAME, "r") as f:
            save_object = json.load(f)
        return save_object, False

def save(save_object):
    with open(SAVE_FILENAME, "w") as f:
        json.dump(save_object, f)

def _create_file(course_ids):
    save_object = create_save_object()
    for id in course_ids:
        save_object["courses"][id] = None
    
    save(save_object)
    return save_object
