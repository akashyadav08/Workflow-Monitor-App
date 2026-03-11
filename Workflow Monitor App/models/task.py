import json
import os
import uuid
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tasks.json")
PROGRESS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "progress.json")


def _ensure_data_dir():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


def load_tasks():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH) as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    _ensure_data_dir()
    with open(DATA_PATH, "w") as f:
        json.dump(tasks, f, indent=2)


def create_task(title, description="", subtasks=None, deadline=None,
                cognitive_load=5, urgency=5, impact=5, dependencies=3,
                category="general", resources=None):
    task = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "description": description,
        "subtasks": subtasks or [],
        "deadline": deadline,
        "cognitive_load": cognitive_load,
        "urgency": urgency,
        "impact": impact,
        "dependencies": dependencies,
        "category": category,
        "resources": resources or [],
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "completed_subtasks": [],
    }
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    return task


def update_task(task_id, updates):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t.update(updates)
            save_tasks(tasks)
            return t
    return None


def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)


def complete_subtask(task_id, subtask_index):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if subtask_index not in t.get("completed_subtasks", []):
                t.setdefault("completed_subtasks", []).append(subtask_index)
            save_tasks(tasks)
            _log_progress(task_id, t["title"], subtask_index,
                          t["subtasks"][subtask_index] if subtask_index < len(t["subtasks"]) else "")
            return t
    return None


def uncomplete_subtask(task_id, subtask_index):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if subtask_index in t.get("completed_subtasks", []):
                t["completed_subtasks"].remove(subtask_index)
            save_tasks(tasks)
            return t
    return None


def add_subtask(task_id, text):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t.setdefault("subtasks", []).append(text)
            save_tasks(tasks)
            return t
    return None


def edit_subtask(task_id, subtask_index, new_text):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if 0 <= subtask_index < len(t.get("subtasks", [])):
                t["subtasks"][subtask_index] = new_text
                save_tasks(tasks)
                return t
    return None


def remove_subtask(task_id, subtask_index):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            subtasks = t.get("subtasks", [])
            if 0 <= subtask_index < len(subtasks):
                subtasks.pop(subtask_index)
                # Fix completed_subtasks indices: remove the index and shift higher ones down
                completed = t.get("completed_subtasks", [])
                new_completed = []
                for c in completed:
                    if c < subtask_index:
                        new_completed.append(c)
                    elif c > subtask_index:
                        new_completed.append(c - 1)
                    # c == subtask_index is dropped (removed subtask)
                t["completed_subtasks"] = new_completed
                save_tasks(tasks)
                return t
    return None


def get_task(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None


def get_progress(task):
    total = len(task.get("subtasks", []))
    if total == 0:
        return 0.0
    done = len(task.get("completed_subtasks", []))
    return done / total


def _log_progress(task_id, task_title, subtask_index, subtask_name):
    _ensure_data_dir()
    log = []
    if os.path.exists(PROGRESS_PATH):
        with open(PROGRESS_PATH) as f:
            log = json.load(f)
    log.append({
        "task_id": task_id,
        "task_title": task_title,
        "subtask_index": subtask_index,
        "subtask_name": subtask_name,
        "completed_at": datetime.now().isoformat(),
    })
    with open(PROGRESS_PATH, "w") as f:
        json.dump(log, f, indent=2)


def load_progress():
    if os.path.exists(PROGRESS_PATH):
        with open(PROGRESS_PATH) as f:
            return json.load(f)
    return []
