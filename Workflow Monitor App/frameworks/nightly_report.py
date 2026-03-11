"""Nightly Report Engine — 10 PM Daily Anchor.

Generates a constructive, forward-looking report that:
1. Celebrates today's wins (no matter how small)
2. Tactically reframes what didn't get done (no guilt, just strategy)
3. Builds momentum for tomorrow with specific, actionable direction
4. Grounds you with a motivational anchor thought

Grounded in: Progress Principle (Amabile), Self-Compassion Theory (Neff),
Implementation Intentions (Gollwitzer), and Growth Mindset (Dweck).
"""

import json
import os
import random
from datetime import datetime, date

REPORTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reports.json")


# ── Anchor messages — the closing thought that sticks ─────────────────────────

ANCHOR_MESSAGES = [
    {
        "quote": "You don't have to be great to start, but you have to start to be great.",
        "author": "Zig Ziglar",
        "reflection": "Today you started. That alone separates you from everyone who only planned to. Tomorrow, you start again — with more momentum than today.",
    },
    {
        "quote": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs",
        "reflection": "You showed up today for work that matters to you. That's not discipline — that's alignment. Tomorrow, lean into the parts that pull your curiosity hardest.",
    },
    {
        "quote": "It does not matter how slowly you go as long as you do not stop.",
        "author": "Confucius",
        "reflection": "Progress is not measured in speed but in consistency. Every day you move forward is a day your future self thanks you for.",
    },
    {
        "quote": "Success is the sum of small efforts, repeated day in and day out.",
        "author": "Robert Collier",
        "reflection": "Today's effort is one brick. You can't see the building yet, but the foundation is getting stronger with every session you complete.",
    },
    {
        "quote": "What you get by achieving your goals is not as important as what you become by achieving your goals.",
        "author": "Henry David Thoreau",
        "reflection": "The skills you're building — focus, consistency, problem-solving — compound far beyond any single task. You're becoming the person who can handle what's next.",
    },
    {
        "quote": "Fall seven times, stand up eight.",
        "author": "Japanese Proverb",
        "reflection": "If today was hard, that's data — not a verdict. Resilience isn't about avoiding hard days; it's about showing up the morning after one.",
    },
    {
        "quote": "The best time to plant a tree was 20 years ago. The second best time is now.",
        "author": "Chinese Proverb",
        "reflection": "Whatever you didn't finish today, tomorrow is the second best time. No guilt, just another chance to move forward.",
    },
    {
        "quote": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.",
        "author": "Aristotle (via Will Durant)",
        "reflection": "Today was one more repetition in the habit of excellence. Each day you show up makes the next day easier. The compound effect is real and it's working.",
    },
    {
        "quote": "Your future is created by what you do today, not tomorrow.",
        "author": "Robert Kiyosaki",
        "reflection": "Today's work is already shaping your future. Sleep well knowing that tomorrow you'll build on what you did today.",
    },
    {
        "quote": "The secret of getting ahead is getting started.",
        "author": "Mark Twain",
        "reflection": "Tomorrow, when resistance shows up (and it will), remember: you just need to start. The first 5 minutes unlock the next 5 hours.",
    },
]

# ── Tactical reframes for missed work ─────────────────────────────────────────

TASK_REFRAMES = {
    "job_applications": {
        "reframe": "Job searching is a marathon, not a sprint. The market doesn't reset overnight — every application you've already sent is still working for you. Tomorrow, pick up exactly where you left off.",
        "tomorrow_action": "Start with one targeted application first thing. Momentum from that single action will carry the rest of the session.",
    },
    "imc_competition": {
        "reframe": "Competition prep is about depth over coverage. Missing a session doesn't erase what you've already learned — spaced repetition research shows a gap can actually improve long-term retention of previously studied material.",
        "tomorrow_action": "Begin with a 10-minute review of your last session's notes. The Zeigarnik effect means your brain has been processing this in the background.",
    },
    "frm_exam": {
        "reframe": "FRM preparation is cumulative. One missed day in a months-long study plan is noise, not signal. Your knowledge doesn't decay overnight — it consolidates during rest (Walker, 2017).",
        "tomorrow_action": "Start with 5 flashcards from previously studied material. Easy wins rebuild study momentum faster than jumping into new content.",
    },
    "allocq": {
        "reframe": "Building is non-linear. Some of the best architectural insights come after stepping away. Your subconscious has been working on this — the default mode network (Buckner, 2008) processes complex problems during downtime.",
        "tomorrow_action": "Write down the ONE thing that would unblock your next feature before opening any code. Clarity first, coding second.",
    },
    "general": {
        "reframe": "Not every day will be a high-output day, and that's expected — not a failure. Research on ultradian rhythms shows productivity naturally ebbs and flows. What matters is the weekly trend, not any single day.",
        "tomorrow_action": "Pick the single highest-impact subtask and commit to completing just that one. One deliberate completion beats five half-starts.",
    },
}


class NightlyReportEngine:
    """Generates the 10 PM nightly report."""

    MAX_SAVED_REPORTS = 5

    def generate_report(self, tasks, progress_log):
        """Generate the full nightly report.

        Args:
            tasks: List of all task dicts
            progress_log: List of progress entries from progress.json

        Returns:
            dict with report sections
        """
        today = date.today().isoformat()
        today_entries = [
            e for e in progress_log
            if e.get("completed_at", "").startswith(today)
        ]

        # Deduplicate by (task_id, subtask_index) — keep latest
        seen = set()
        unique_completions = []
        for entry in reversed(today_entries):
            key = (entry["task_id"], entry["subtask_index"])
            if key not in seen:
                seen.add(key)
                unique_completions.append(entry)
        unique_completions.reverse()

        active_tasks = [t for t in tasks if t.get("status") == "active"]

        # Build report sections
        wins = self._build_wins(active_tasks, unique_completions)
        tactical = self._build_tactical_reframes(active_tasks, unique_completions)
        tomorrow = self._build_tomorrow_plan(active_tasks, unique_completions)
        anchor = self._select_anchor(wins, unique_completions)
        summary = self._build_summary(active_tasks, unique_completions)

        # Build broader outlook from past reports
        past_reports = self._load_reports()
        broader_outlook = self._build_broader_outlook(past_reports, summary, unique_completions, active_tasks)

        report = {
            "generated_at": datetime.now().isoformat(),
            "date": today,
            "summary": summary,
            "wins": wins,
            "tactical_reframes": tactical,
            "tomorrow_plan": tomorrow,
            "broader_outlook": broader_outlook,
            "anchor": anchor,
        }

        # Save report (keep only last 5)
        self._save_report(report, past_reports)

        return report

    # ── Report persistence ────────────────────────────────────────────────

    def _load_reports(self):
        """Load saved reports from disk."""
        if os.path.exists(REPORTS_PATH):
            with open(REPORTS_PATH) as f:
                return json.load(f)
        return []

    def _save_report(self, report, past_reports):
        """Save report, keeping only the last 5."""
        os.makedirs(os.path.dirname(REPORTS_PATH), exist_ok=True)

        # Don't save duplicate for same date — replace if exists
        reports = [r for r in past_reports if r.get("date") != report.get("date")]
        reports.append(report)

        # Keep only the most recent MAX_SAVED_REPORTS
        reports = reports[-self.MAX_SAVED_REPORTS:]

        with open(REPORTS_PATH, "w") as f:
            json.dump(reports, f, indent=2)

    def get_saved_reports(self):
        """Return all saved reports (up to 5)."""
        return self._load_reports()

    def wipe_reports(self):
        """Delete all saved reports."""
        if os.path.exists(REPORTS_PATH):
            os.remove(REPORTS_PATH)
        return {"status": "wiped", "message": "All previous reports cleared."}

    # ── Broader Outlook ───────────────────────────────────────────────────

    def _build_broader_outlook(self, past_reports, today_summary, today_completions, active_tasks):
        """Analyze trends across saved reports for a wider perspective."""
        if not past_reports:
            return {
                "has_history": False,
                "message": "This is your first nightly report. From tomorrow, you'll start seeing trends across days — completion patterns, momentum shifts, and your consistency streak. The data starts now.",
                "streak": 0,
                "trend": None,
                "task_coverage": None,
                "consistency_note": None,
            }

        # Completion counts per day from past reports
        daily_counts = []
        for r in past_reports:
            wins = r.get("wins", {})
            if wins.get("has_wins"):
                count = sum(item.get("count_today", 0) for item in wins.get("items", []))
            else:
                count = 0
            daily_counts.append({
                "date": r.get("date", ""),
                "count": count,
                "tone": r.get("summary", {}).get("tone", "gentle"),
            })

        # Add today
        today_count = len(today_completions)
        daily_counts.append({
            "date": date.today().isoformat(),
            "count": today_count,
            "tone": today_summary.get("tone", "gentle"),
        })

        # Streak: consecutive days with at least 1 completion
        streak = 0
        for entry in reversed(daily_counts):
            if entry["count"] > 0:
                streak += 1
            else:
                break

        # Trend: compare today vs average of past
        past_counts = [d["count"] for d in daily_counts[:-1]]
        avg_past = sum(past_counts) / len(past_counts) if past_counts else 0
        if today_count > avg_past * 1.2:
            trend = "upward"
            trend_message = f"Today's {today_count} completions beat your recent average of {avg_past:.1f}. You're trending upward — momentum is building."
        elif today_count < avg_past * 0.8 and avg_past > 0:
            trend = "dip"
            trend_message = f"Today was lighter ({today_count}) vs your recent average ({avg_past:.1f}). Dips are natural — research on ultradian rhythms shows productivity is cyclical. What matters is that you keep showing up."
        else:
            trend = "steady"
            trend_message = f"You're holding steady around {avg_past:.1f} completions per day. Consistency is the most underrated superpower — Ericsson's deliberate practice research shows it beats intensity every time."

        # Task coverage across recent reports — which tasks get love, which get neglected
        task_hit_counts = {}
        for r in past_reports:
            wins = r.get("wins", {})
            for item in wins.get("items", []):
                title = item.get("task_title", "")
                if title:
                    task_hit_counts[title] = task_hit_counts.get(title, 0) + 1

        # Add today's
        for item in (self._build_wins(active_tasks, today_completions).get("items", []) if today_completions else []):
            title = item.get("task_title", "")
            if title:
                task_hit_counts[title] = task_hit_counts.get(title, 0) + 1

        total_days = len(daily_counts)
        coverage = []
        for task in active_tasks:
            hits = task_hit_counts.get(task["title"], 0)
            coverage.append({
                "task_title": task["title"],
                "days_active": hits,
                "total_days": total_days,
                "coverage_pct": round((hits / total_days) * 100) if total_days else 0,
            })

        # Consistency note
        if streak >= 5:
            consistency_note = f"{streak}-day streak! You've shown up every single day. This is the compound effect in action — each day makes the next one easier."
        elif streak >= 3:
            consistency_note = f"{streak}-day streak. You're building a real habit. Research shows it takes ~66 days to form a habit (Lally, 2009), and you're stacking days."
        elif streak == 1 and today_count > 0:
            consistency_note = "Day 1 of a new streak. Every streak starts with one. Tomorrow, make it two."
        elif streak == 0:
            consistency_note = "The streak resets — but so does the opportunity. Tomorrow is day 1 again, and that's all you need."
        else:
            consistency_note = f"{streak} days running. Keep the chain going."

        # Overall message
        num_past = len(past_reports)
        message = f"Looking across your last {num_past + 1} report{'s' if num_past > 0 else ''}: {trend_message}"

        return {
            "has_history": True,
            "message": message,
            "streak": streak,
            "trend": trend,
            "trend_message": trend_message,
            "daily_counts": daily_counts,
            "task_coverage": coverage,
            "consistency_note": consistency_note,
            "reports_saved": len(past_reports),
        }

    def _build_summary(self, tasks, completions):
        """One-line summary of the day."""
        count = len(completions)
        task_names = list({c["task_title"] for c in completions})

        if count == 0:
            return {
                "headline": "Rest day — and that's valid",
                "detail": "No subtasks were completed today, but showing up to check in still counts. Tomorrow is a fresh canvas.",
                "tone": "gentle",
            }
        elif count <= 2:
            return {
                "headline": f"{count} subtask{'s' if count > 1 else ''} completed — steady progress",
                "detail": f"You moved forward on {', '.join(task_names)}. Small steps compound. This is exactly how progress works.",
                "tone": "encouraging",
            }
        elif count <= 5:
            return {
                "headline": f"{count} subtasks completed — solid day",
                "detail": f"Real momentum across {', '.join(task_names)}. You're building the kind of consistency that produces results.",
                "tone": "strong",
            }
        else:
            return {
                "headline": f"{count} subtasks completed — exceptional output",
                "detail": f"You crushed it across {', '.join(task_names)}. Days like this are the ones that compound into breakthroughs. Well earned.",
                "tone": "celebration",
            }

    def _build_wins(self, tasks, completions):
        """Celebrate what was accomplished today."""
        if not completions:
            return {
                "has_wins": False,
                "message": "No subtasks completed today — but you checked in, and self-awareness is the foundation of all progress. Kristin Neff's self-compassion research shows that self-kindness after a low day predicts better performance tomorrow far more than self-criticism does.",
                "items": [],
            }

        # Group completions by task
        by_task = {}
        for c in completions:
            tid = c["task_id"]
            if tid not in by_task:
                by_task[tid] = {"title": c["task_title"], "subtasks": []}
            by_task[tid]["subtasks"].append(c["subtask_name"])

        items = []
        for tid, data in by_task.items():
            task = next((t for t in tasks if t["id"] == tid), None)
            total = len(task["subtasks"]) if task else "?"
            completed_total = len(task.get("completed_subtasks", [])) if task else "?"
            pct = round((completed_total / total) * 100) if task and total else 0

            items.append({
                "task_title": data["title"],
                "completed_today": data["subtasks"],
                "count_today": len(data["subtasks"]),
                "overall_progress": f"{completed_total}/{total} ({pct}%)",
            })

        total_done = len(completions)
        message = self._wins_message(total_done, items)

        return {
            "has_wins": True,
            "message": message,
            "items": items,
        }

    def _wins_message(self, total, items):
        task_count = len(items)
        if total == 1:
            return f"You completed 1 subtask today. That's one more than zero — and the Progress Principle research (Amabile, 2011) shows that even a single small win is the strongest driver of motivation and positive inner work life. This win counts."
        elif task_count == 1:
            return f"You completed {total} subtasks on {items[0]['task_title']}. Focused effort on a single area builds deep momentum. You're making the kind of concentrated progress that leads to breakthroughs."
        else:
            names = [i["task_title"] for i in items]
            return f"You completed {total} subtasks across {task_count} different tasks ({', '.join(names)}). Breadth AND depth — you're advancing on multiple fronts while keeping each one moving."

    def _build_tactical_reframes(self, tasks, completions):
        """Constructive reframes for tasks that didn't see progress today."""
        completed_task_ids = {c["task_id"] for c in completions}
        missed_tasks = [
            t for t in tasks
            if t["id"] not in completed_task_ids and t.get("status") == "active"
        ]

        if not missed_tasks:
            return {
                "has_misses": False,
                "message": "You touched every active task today. That's rare and impressive — full coverage across your portfolio.",
                "items": [],
            }

        items = []
        for task in missed_tasks:
            category = task.get("category", "general")
            reframe_data = TASK_REFRAMES.get(category, TASK_REFRAMES["general"])

            # Get next incomplete subtask for specificity
            completed_set = set(task.get("completed_subtasks", []))
            next_subtask = None
            for i, st in enumerate(task.get("subtasks", [])):
                if i not in completed_set:
                    next_subtask = st
                    break

            items.append({
                "task_title": task["title"],
                "category": category,
                "reframe": reframe_data["reframe"],
                "tomorrow_action": reframe_data["tomorrow_action"],
                "next_subtask": next_subtask,
                "total_remaining": len(task.get("subtasks", [])) - len(completed_set),
            })

        count = len(items)
        message = f"{count} task{'s' if count > 1 else ''} didn't see progress today. That's not failure — it's prioritization. You can't do everything every day, and research on decision fatigue (Baumeister, 2011) confirms that selective focus produces better outcomes than thin coverage across too many fronts."

        return {
            "has_misses": True,
            "message": message,
            "items": items,
        }

    def _build_tomorrow_plan(self, tasks, completions):
        """Build a forward-looking plan for tomorrow."""
        # Identify the task with most momentum (most completions today)
        momentum_task = None
        if completions:
            task_counts = {}
            for c in completions:
                task_counts[c["task_id"]] = task_counts.get(c["task_id"], 0) + 1
            momentum_id = max(task_counts, key=task_counts.get)
            momentum_task = next((t for t in tasks if t["id"] == momentum_id), None)

        # Identify the task most in need (least progress, highest urgency)
        needs_attention = None
        max_need_score = -1
        for task in tasks:
            if task.get("status") != "active":
                continue
            total = len(task.get("subtasks", []))
            done = len(task.get("completed_subtasks", []))
            if total == 0:
                continue
            progress = done / total
            urgency = task.get("urgency", 5)
            need_score = urgency * (1 - progress)
            if need_score > max_need_score:
                max_need_score = need_score
                needs_attention = task

        plan_items = []

        # Momentum continuation
        if momentum_task:
            completed_set = set(momentum_task.get("completed_subtasks", []))
            next_subs = []
            for i, st in enumerate(momentum_task.get("subtasks", [])):
                if i not in completed_set:
                    next_subs.append(st)
                    if len(next_subs) >= 2:
                        break

            plan_items.append({
                "type": "momentum",
                "title": f"Ride the momentum on {momentum_task['title']}",
                "rationale": "You made real progress here today. The goal gradient effect (Hull, 1932) means your brain is primed to continue — effort increases as you get closer to completion.",
                "suggested_subtasks": next_subs,
            })

        # Needs attention
        if needs_attention and (not momentum_task or needs_attention["id"] != momentum_task["id"]):
            completed_set = set(needs_attention.get("completed_subtasks", []))
            next_sub = None
            for i, st in enumerate(needs_attention.get("subtasks", [])):
                if i not in completed_set:
                    next_sub = st
                    break

            plan_items.append({
                "type": "needs_attention",
                "title": f"Give some love to {needs_attention['title']}",
                "rationale": f"This task has high urgency ({needs_attention.get('urgency', '?')}/10) and could use forward motion. Even one subtask completed here changes the trajectory.",
                "suggested_subtasks": [next_sub] if next_sub else [],
            })

        # Implementation intention for tomorrow morning
        first_task = momentum_task or needs_attention or (tasks[0] if tasks else None)
        intention = None
        if first_task:
            intention = f"When I sit down tomorrow morning, the FIRST thing I will do is open {first_task['title']} and work on the next incomplete subtask for 15 minutes before checking anything else."

        return {
            "plan_items": plan_items,
            "implementation_intention": intention,
            "principle": "Gollwitzer (1999): Pre-committing to a specific if-then plan ('When X happens, I will do Y') doubles to triples follow-through rates. Setting your intention tonight means tomorrow's decision is already made.",
        }

    def _select_anchor(self, wins, completions):
        """Select the closing anchor thought."""
        # Pick an anchor that matches the day's tone
        if not completions:
            # Gentle anchors for rest days
            candidates = [a for a in ANCHOR_MESSAGES if "start" in a["quote"].lower() or "stop" in a["quote"].lower() or "slowly" in a["quote"].lower()]
        elif len(completions) >= 5:
            # Celebratory anchors for big days
            candidates = [a for a in ANCHOR_MESSAGES if "excellence" in a["quote"].lower() or "great work" in a["quote"].lower() or "sum" in a["quote"].lower()]
        else:
            candidates = ANCHOR_MESSAGES

        if not candidates:
            candidates = ANCHOR_MESSAGES

        return random.choice(candidates)
