"""Motivation Catalyst Agent.

Delivers science-based, context-aware motivation using six research frameworks.
Adapts to task type, progress level, and time of day.
"""

from frameworks.motivation_science import MotivationEngine
from frameworks.nightly_report import NightlyReportEngine
from models.task import load_tasks, get_task, get_progress, load_progress


class MotivationAgent:
    """Delivers contextual motivation based on scientific principles."""

    def __init__(self):
        self.engine = MotivationEngine()
        self.report_engine = NightlyReportEngine()

    def get_motivation_for_task(self, task_id, force_framework=None):
        """Get motivation for a specific task."""
        task = get_task(task_id)
        if not task:
            return {"error": "Task not found"}
        progress_pct = get_progress(task)
        return self.engine.get_motivation(task, progress_pct, force_framework=force_framework)

    def get_motivation_for_current_block(self, current_block):
        """Get motivation for whatever task is in the current schedule block."""
        if not current_block or not current_block.get("task_id"):
            return {
                "framework": "Break Science",
                "title": "Rest Is Productive",
                "message": "You're on a break or between tasks. This isn't downtime — it's consolidation time. Research on the default mode network (Buckner et al., 2008) shows the brain actively processes and consolidates learning during rest. Let it work.",
                "principle": "Ultradian rhythms and default mode network research: cognitive performance follows ~90-minute cycles. Rest periods aren't lost time — they're when your brain integrates what you've learned.",
                "action": "Step away from the screen. Move your body. Don't consume new information — let your brain process what it already has.",
            }
        task = get_task(current_block["task_id"])
        if not task:
            return {"error": "Task not found"}
        progress_pct = get_progress(task)
        return self.engine.get_motivation(task, progress_pct)

    def get_all_frameworks_for_task(self, task_id):
        """Get motivation from every framework for a task (for the UI's deep dive view)."""
        task = get_task(task_id)
        if not task:
            return {"error": "Task not found"}
        progress_pct = get_progress(task)
        return self.engine.get_all_motivations(task, progress_pct)

    def get_daily_briefing(self):
        """Generate a morning motivational briefing across all active tasks."""
        tasks = load_tasks()
        active = [t for t in tasks if t.get("status") == "active"]
        briefing = []
        for task in active:
            progress_pct = get_progress(task)
            completed = len(task.get("completed_subtasks", []))
            total = len(task.get("subtasks", []))

            # Pick the most relevant single motivation for each task
            mot = self.engine.get_motivation(task, progress_pct)
            briefing.append({
                "task_id": task["id"],
                "task_title": task["title"],
                "progress": f"{completed}/{total} subtasks",
                "progress_pct": round(progress_pct * 100),
                "motivation": mot,
            })
        return briefing

    def get_nightly_report(self):
        """Generate the 10 PM nightly report — the daily anchor."""
        tasks = load_tasks()
        progress_log = load_progress()
        return self.report_engine.generate_report(tasks, progress_log)

    def get_report_history(self):
        """Return saved past reports."""
        return self.report_engine.get_saved_reports()

    def wipe_reports(self):
        """Delete all saved reports."""
        return self.report_engine.wipe_reports()
