"""Workflow Monitor — Flask Application.

Two-agent system: Workflow Orchestrator + Motivation Catalyst.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, jsonify, request
from agents.workflow_agent import WorkflowAgent
from agents.motivation_agent import MotivationAgent
from models.task import (
    create_task, update_task, delete_task, complete_subtask,
    uncomplete_subtask, get_task, load_tasks, get_progress,
    add_subtask, edit_subtask, remove_subtask,
)
from config import load_settings, save_settings

app = Flask(__name__)
workflow = WorkflowAgent()
motivation = MotivationAgent()


# ── Pages ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Workflow Agent API ─────────────────────────────────────────────────────────

@app.route("/api/dashboard")
def dashboard():
    """Full dashboard data in one call."""
    data = workflow.get_dashboard_data()
    return jsonify(data)


@app.route("/api/tasks")
def get_tasks():
    from frameworks.priority import rank_tasks
    tasks = load_tasks()
    ranked = rank_tasks(tasks)
    for t in ranked:
        t["progress"] = get_progress(t)
    return jsonify(ranked)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.json
    task = create_task(
        title=data["title"],
        description=data.get("description", ""),
        subtasks=data.get("subtasks", []),
        deadline=data.get("deadline"),
        cognitive_load=data.get("cognitive_load", 5),
        urgency=data.get("urgency", 5),
        impact=data.get("impact", 5),
        dependencies=data.get("dependencies", 3),
        category=data.get("category", "general"),
        resources=data.get("resources", []),
    )
    return jsonify(task), 201


@app.route("/api/tasks/<task_id>", methods=["PUT"])
def modify_task(task_id):
    data = request.json
    task = update_task(task_id, data)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def remove_task(task_id):
    delete_task(task_id)
    return jsonify({"status": "deleted"})


@app.route("/api/tasks/<task_id>/complete/<int:subtask_index>", methods=["POST"])
def mark_subtask_complete(task_id, subtask_index):
    task = complete_subtask(task_id, subtask_index)
    if task:
        task["progress"] = get_progress(task)
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404


@app.route("/api/tasks/<task_id>/uncomplete/<int:subtask_index>", methods=["POST"])
def mark_subtask_uncomplete(task_id, subtask_index):
    task = uncomplete_subtask(task_id, subtask_index)
    if task:
        task["progress"] = get_progress(task)
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404


# ── Subtask CRUD ──────────────────────────────────────────────────────────────

@app.route("/api/tasks/<task_id>/subtasks", methods=["POST"])
def add_subtask_route(task_id):
    data = request.json
    task = add_subtask(task_id, data.get("text", ""))
    if task:
        task["progress"] = get_progress(task)
        return jsonify(task), 201
    return jsonify({"error": "Task not found"}), 404


@app.route("/api/tasks/<task_id>/subtasks/<int:index>", methods=["PUT"])
def edit_subtask_route(task_id, index):
    data = request.json
    task = edit_subtask(task_id, index, data.get("text", ""))
    if task:
        task["progress"] = get_progress(task)
        return jsonify(task)
    return jsonify({"error": "Task or subtask not found"}), 404


@app.route("/api/tasks/<task_id>/subtasks/<int:index>", methods=["DELETE"])
def remove_subtask_route(task_id, index):
    task = remove_subtask(task_id, index)
    if task:
        task["progress"] = get_progress(task)
        return jsonify(task)
    return jsonify({"error": "Task or subtask not found"}), 404


# ── Resources ──────────────────────────────────────────────────────────────────

@app.route("/api/resources/<task_id>")
def task_resources(task_id):
    data = workflow.get_resources(task_id)
    if data:
        return jsonify(data)
    return jsonify({"error": "Task not found"}), 404


@app.route("/api/resources")
def all_resources():
    return jsonify(workflow.get_all_resources())


# ── Motivation Agent API ───────────────────────────────────────────────────────

@app.route("/api/motivation/<task_id>")
def get_motivation(task_id):
    framework = request.args.get("framework")
    data = motivation.get_motivation_for_task(task_id, force_framework=framework)
    return jsonify(data)


@app.route("/api/motivation/<task_id>/all")
def get_all_motivations(task_id):
    data = motivation.get_all_frameworks_for_task(task_id)
    return jsonify(data)


@app.route("/api/motivation/current")
def get_current_motivation():
    dashboard_data = workflow.get_dashboard_data()
    current = dashboard_data.get("current_block")
    data = motivation.get_motivation_for_current_block(current)
    return jsonify(data)


@app.route("/api/motivation/briefing")
def get_briefing():
    data = motivation.get_daily_briefing()
    return jsonify(data)


@app.route("/api/progress/monthly")
def get_monthly_progress():
    """Return per-day completion counts for the current month."""
    from models.task import load_progress
    from datetime import date
    import calendar

    progress_log = load_progress()
    today = date.today()
    year, month = today.year, today.month
    prefix = f"{year}-{month:02d}"
    days_in_month = calendar.monthrange(year, month)[1]

    # Count unique completions per day
    daily = {}
    for entry in progress_log:
        ts = entry.get("completed_at", "")
        if ts.startswith(prefix):
            day_str = ts[:10]
            key = (entry["task_id"], entry["subtask_index"], day_str)
            daily.setdefault(day_str, set()).add(key)

    # Build result for every day of the month
    days = []
    for d in range(1, days_in_month + 1):
        day_str = f"{year}-{month:02d}-{d:02d}"
        count = len(daily.get(day_str, set()))
        is_today = (d == today.day)
        is_future = (d > today.day)
        days.append({
            "date": day_str,
            "day": d,
            "count": count,
            "is_today": is_today,
            "is_future": is_future,
        })

    # Weekday of 1st (0=Mon, 6=Sun)
    first_weekday = calendar.monthrange(year, month)[0]  # 0=Mon
    # Shift to Sun-start: Sun=0
    first_weekday_sun = (first_weekday + 1) % 7

    return jsonify({
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "days_in_month": days_in_month,
        "first_weekday": first_weekday_sun,
        "days": days,
        "max_count": max((d["count"] for d in days), default=0),
    })


@app.route("/api/report/nightly")
def get_nightly_report():
    """Generate the 10 PM nightly anchor report."""
    data = motivation.get_nightly_report()
    return jsonify(data)


@app.route("/api/report/history")
def get_report_history():
    """Return the last 5 saved nightly reports."""
    data = motivation.get_report_history()
    return jsonify(data)


@app.route("/api/report/wipe", methods=["POST"])
def wipe_reports():
    """Delete all saved reports."""
    data = motivation.wipe_reports()
    return jsonify(data)


# ── Settings ───────────────────────────────────────────────────────────────────

@app.route("/api/settings")
def get_settings():
    return jsonify(load_settings())


@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.json
    settings = workflow.update_settings(data)
    return jsonify(settings)


@app.route("/api/settings/toggle-mode", methods=["POST"])
def toggle_mode():
    new_mode = workflow.toggle_energy_mode()
    return jsonify({"energy_mode": new_mode})


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  🧠 Workflow Monitor — Two-Agent System")
    print("  ═══════════════════════════════════════")
    print("  Agent 1: Workflow Orchestrator (tasks, schedule, resources)")
    print("  Agent 2: Motivation Catalyst (science-based motivation)")
    print("  ─────────────────────────────────────────────────────────")
    print("  Running at: http://localhost:5050\n")
    app.run(debug=True, port=5050)
