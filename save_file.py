from tempfile import NamedTemporaryFile
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
        
        save_object = _change_tracked_courses(save_object, course_ids)
        return save_object, False

def save(save_object):
    try:
        with NamedTemporaryFile("w", dir=".", delete=False) as f:
            json.dump(save_object, f)
        if os.path.isfile(SAVE_FILENAME):
            os.replace(f.name, SAVE_FILENAME)
        else:
            os.rename(f.name, SAVE_FILENAME)

    except:
        if f.name != SAVE_FILENAME:
            os.remove(f.name)
        raise
    

def _create_file(course_ids):
    save_object = create_save_object()
    for id in course_ids:
        save_object["courses"][id] = None
    
    save(save_object)
    return save_object

def _change_tracked_courses(save_object, course_ids):
    courses: dict = save_object["courses"]
    for id in courses.copy():
        if id not in course_ids:
            del courses[id]
    
    for id in course_ids:
        if id not in courses:
            courses[id] = None
    
    print(save_object)
    return save_object