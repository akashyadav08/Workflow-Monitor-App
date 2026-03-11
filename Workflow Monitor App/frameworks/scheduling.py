from datetime import datetime, timedelta


def _t(time_str):
    """Parse HH:MM to datetime (today)."""
    h, m = map(int, time_str.split(":"))
    return datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)


def generate_schedule(ranked_tasks, settings):
    """Generate daily time blocks based on ranked tasks and energy mode.

    Returns a list of schedule blocks:
    [{"start": "09:30", "end": "10:15", "task_id": ..., "task_title": ...,
      "type": "work"|"break"|"call"|"review", "focus_subtasks": [...]}]
    """
    mode = settings.get("energy_mode", "morning")
    family_call = settings.get("family_call", {"start": "16:00", "end": "16:30"})

    if mode == "morning":
        return _morning_schedule(ranked_tasks, settings, family_call)
    else:
        return _night_owl_schedule(ranked_tasks, settings, family_call)


def _get_task_by_category(ranked_tasks, category):
    for t in ranked_tasks:
        if t.get("category") == category:
            return t
    return None


def _block(start, end, task=None, block_type="work", label=None, focus_subtasks=None):
    return {
        "start": start,
        "end": end,
        "task_id": task["id"] if task else None,
        "task_title": label or (task["title"] if task else ""),
        "type": block_type,
        "category": task.get("category", "") if task else "",
        "focus_subtasks": focus_subtasks or [],
        "cognitive_load": task.get("cognitive_load", 5) if task else 0,
    }


def _get_incomplete_subtasks(task, limit=3):
    """Get the next incomplete subtasks for a task."""
    completed = set(task.get("completed_subtasks", []))
    subtasks = task.get("subtasks", [])
    result = []
    for i, st in enumerate(subtasks):
        if i not in completed:
            result.append(st)
            if len(result) >= limit:
                break
    return result


def _morning_schedule(ranked_tasks, settings, family_call):
    """Morning person schedule: deep analytical work early, creative afternoon."""
    jobs = _get_task_by_category(ranked_tasks, "job_applications")
    imc = _get_task_by_category(ranked_tasks, "imc_competition")
    allocq = _get_task_by_category(ranked_tasks, "allocq")
    frm = _get_task_by_category(ranked_tasks, "frm_exam")

    schedule = []

    # 09:30 - 10:15 : Job Applications
    if jobs:
        schedule.append(_block("09:30", "10:15", jobs,
                               focus_subtasks=_get_incomplete_subtasks(jobs)))

    # 10:15 - 10:30 : Break
    schedule.append(_block("10:15", "10:30", block_type="break", label="Break — stretch & hydrate"))

    # 10:30 - 12:30 : IMC Competition Prep (deep work block 1)
    if imc:
        schedule.append(_block("10:30", "12:30", imc,
                               focus_subtasks=_get_incomplete_subtasks(imc)))

    # 12:30 - 13:30 : Lunch
    schedule.append(_block("12:30", "13:30", block_type="break", label="Lunch — step away from screen"))

    # 13:30 - 15:30 : AllocQ Building
    if allocq:
        schedule.append(_block("13:30", "15:30", allocq,
                               focus_subtasks=_get_incomplete_subtasks(allocq)))

    # 15:30 - 15:45 : Break
    schedule.append(_block("15:30", "15:45", block_type="break", label="Break — move around"))

    # 15:45 - 16:00 : Buffer / prep for call
    schedule.append(_block("15:45", "16:00", block_type="break", label="Wind down — prep for family call"))

    # 16:00 - 16:30 : Family call
    schedule.append(_block("16:00", "16:30", block_type="call", label="Family call"))

    # 16:30 - 16:45 : Break
    schedule.append(_block("16:30", "16:45", block_type="break", label="Post-call transition"))

    # 16:45 - 18:15 : FRM Study
    if frm:
        schedule.append(_block("16:45", "18:15", frm,
                               focus_subtasks=_get_incomplete_subtasks(frm)))

    # 18:15 - 18:30 : Break
    schedule.append(_block("18:15", "18:30", block_type="break", label="Break — refresh"))

    # 18:30 - 19:45 : Flex block (IMC overflow or task with most remaining work)
    flex_task = imc or frm
    if flex_task:
        schedule.append(_block("18:30", "19:45", flex_task,
                               label=f"{flex_task['title']} (flex/overflow)",
                               focus_subtasks=_get_incomplete_subtasks(flex_task)))

    # 19:45 - 20:00 : Daily review
    schedule.append(_block("19:45", "20:00", block_type="review", label="Daily review — log progress & plan tomorrow"))

    return schedule


def _night_owl_schedule(ranked_tasks, settings, family_call):
    """Night owl schedule: warm-up with lighter tasks, deep work afternoon/evening."""
    jobs = _get_task_by_category(ranked_tasks, "job_applications")
    imc = _get_task_by_category(ranked_tasks, "imc_competition")
    allocq = _get_task_by_category(ranked_tasks, "allocq")
    frm = _get_task_by_category(ranked_tasks, "frm_exam")

    schedule = []

    # 09:30 - 10:15 : FRM warm-up (structured, lower barrier)
    if frm:
        schedule.append(_block("09:30", "10:15", frm,
                               label=f"{frm['title']} (warm-up review)",
                               focus_subtasks=_get_incomplete_subtasks(frm)))

    # 10:15 - 10:30 : Break
    schedule.append(_block("10:15", "10:30", block_type="break", label="Break — coffee & stretch"))

    # 10:30 - 11:15 : Job Applications
    if jobs:
        schedule.append(_block("10:30", "11:15", jobs,
                               focus_subtasks=_get_incomplete_subtasks(jobs)))

    # 11:15 - 11:30 : Break
    schedule.append(_block("11:15", "11:30", block_type="break", label="Break — move around"))

    # 11:30 - 13:00 : AllocQ Building (creative energy building)
    if allocq:
        schedule.append(_block("11:30", "13:00", allocq,
                               focus_subtasks=_get_incomplete_subtasks(allocq)))

    # 13:00 - 14:00 : Lunch
    schedule.append(_block("13:00", "14:00", block_type="break", label="Lunch — step away from screen"))

    # 14:00 - 16:00 : IMC Competition Prep (peak analytical for night owls)
    if imc:
        schedule.append(_block("14:00", "16:00", imc,
                               focus_subtasks=_get_incomplete_subtasks(imc)))

    # 16:00 - 16:30 : Family call
    schedule.append(_block("16:00", "16:30", block_type="call", label="Family call"))

    # 16:30 - 16:45 : Break
    schedule.append(_block("16:30", "16:45", block_type="break", label="Post-call transition"))

    # 16:45 - 18:45 : IMC Competition Prep (deep work block 2)
    if imc:
        schedule.append(_block("16:45", "18:45", imc,
                               label=f"{imc['title']} (deep work continued)",
                               focus_subtasks=_get_incomplete_subtasks(imc)))

    # 18:45 - 19:00 : Break
    schedule.append(_block("18:45", "19:00", block_type="break", label="Break — refresh"))

    # 19:00 - 19:45 : FRM deep study (evening consolidation)
    if frm:
        schedule.append(_block("19:00", "19:45", frm,
                               label=f"{frm['title']} (deep review)",
                               focus_subtasks=_get_incomplete_subtasks(frm)))

    # 19:45 - 20:00 : Daily review
    schedule.append(_block("19:45", "20:00", block_type="review", label="Daily review — log progress & plan tomorrow"))

    return schedule


def get_current_block(schedule):
    """Return the current schedule block based on current time, or None."""
    now = datetime.now()
    for block in schedule:
        start = _t(block["start"])
        end = _t(block["end"])
        if start <= now < end:
            return block
    return None


def get_next_block(schedule):
    """Return the next upcoming work block."""
    now = datetime.now()
    for block in schedule:
        start = _t(block["start"])
        if start > now and block["type"] == "work":
            return block
    return None
