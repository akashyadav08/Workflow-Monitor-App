import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data", "settings.json")

DEFAULT_SETTINGS = {
    "energy_mode": "morning",  # "morning" or "night_owl"
    "work_start": "09:30",
    "work_end": "20:00",
    "family_call": {"start": "16:00", "end": "16:30"},
    "break_duration_minutes": 15,
    "lunch_duration_minutes": 60,
    "deep_work_block_minutes": 120,
    "review_block_minutes": 15,
}


def load_settings():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            saved = json.load(f)
        merged = {**DEFAULT_SETTINGS, **saved}
        return merged
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(settings, f, indent=2)
    return settings
