"""Workflow Orchestrator Agent.

Manages tasks, generates schedules, tracks progress, and provides resources.
"""

from models.task import (
    load_tasks, save_tasks, create_task, update_task, delete_task,
    complete_subtask, uncomplete_subtask, get_task, get_progress, load_progress,
)
from frameworks.priority import rank_tasks
from frameworks.scheduling import generate_schedule, get_current_block, get_next_block
from config import load_settings, save_settings


# ── Curated resources per task category ────────────────────────────────────────

RESOURCES = {
    "job_applications": {
        "platforms": [
            {"name": "Mercor", "url": "https://mercor.com", "note": "AI-matched job platform — good for tech/quant roles"},
            {"name": "Seek", "url": "https://seek.com.au", "note": "Australia's largest job board — filter by remote, sponsorship"},
            {"name": "LinkedIn Jobs", "url": "https://linkedin.com/jobs", "note": "Use Boolean search: 'quantitative OR data OR python' AND 'Australia OR remote'"},
        ],
        "tips": [
            "Tailor each application's first 2 sentences to the specific company — recruiters spend ~7 seconds on initial scan",
            "For Australian roles, emphasize timezone overlap and remote collaboration experience",
            "Apply early in the week (Mon-Wed) — response rates are 10-20% higher than late-week applications",
            "On Mercor, complete all profile assessments — they weight these heavily in matching",
        ],
        "learning": [
            {"title": "Australian Resume Format Guide", "type": "guide", "note": "AU format differs from US — no photo, include visa status if applicable"},
        ],
    },
    "imc_competition": {
        "core_reading": [
            {"title": "Trading and Exchanges — Larry Harris", "type": "book", "note": "Ch. 4-7 on order types, orderbook mechanics, and market microstructure"},
            {"title": "IMC Prosperity 3 Wiki & Past Rounds", "type": "reference", "note": "Review past round structures, scoring, and community strategies"},
            {"title": "Options, Futures, and Other Derivatives — Hull", "type": "book", "note": "Ch. 10-13 for Black-Scholes, Greeks, and hedging strategies"},
        ],
        "orderbook_resources": [
            {"title": "Orderbook Dynamics & Market Microstructure (Bouchaud et al.)", "type": "paper", "note": "Price impact, order flow, bid-ask dynamics"},
            {"title": "QuantConnect Lean Engine", "type": "tool", "note": "Backtest orderbook strategies with L2 data"},
            {"title": "Lobster Data (academic orderbook data)", "type": "dataset", "note": "High-frequency limit order book data for analysis practice"},
        ],
        "market_inefficiencies": [
            {"title": "Statistical Arbitrage — Avellaneda & Lee", "type": "paper", "note": "Pairs trading and mean reversion strategies"},
            {"title": "Market Making under Asymmetric Information — Glosten & Milgrom", "type": "paper", "note": "Foundation for understanding adverse selection in orderbooks"},
            {"title": "Momentum and Mean Reversion in IMC-style Competitions", "type": "strategy", "note": "Focus on identifying regime changes: trending vs. mean-reverting"},
        ],
        "options_models": [
            {"title": "Black-Scholes Implementation (Python)", "type": "tutorial", "note": "Build from scratch to internalize the math"},
            {"title": "Volatility Surface Modeling", "type": "topic", "note": "Implied vol, vol smile, term structure — key for options mispricing"},
            {"title": "Delta Hedging & Gamma Scalping", "type": "strategy", "note": "Core strategies for options market-making in competition format"},
            {"title": "Monte Carlo Methods for Options Pricing", "type": "tutorial", "note": "Useful for exotic options and path-dependent payoffs"},
        ],
        "algorithms": [
            {"title": "Market Making Algorithms — Avellaneda-Stoikov", "type": "paper", "note": "Optimal bid-ask placement under inventory risk"},
            {"title": "Optimal Execution — Almgren-Chriss", "type": "paper", "note": "Minimize market impact when building/unwinding positions"},
        ],
    },
    "frm_exam": {
        "primary": [
            {"title": "Schweser FRM Part 2 Notes", "type": "study_notes", "note": "Concise summaries of all topics — use as primary review material"},
            {"title": "GARP Official Practice Exams", "type": "practice", "note": "Closest to actual exam format — save for final 4 weeks"},
            {"title": "Bionic Turtle FRM Study Notes & Forum", "type": "community", "note": "David Harper's explanations are excellent for difficult concepts"},
        ],
        "by_topic": [
            {"title": "Market Risk — Value at Risk (Jorion)", "type": "book", "note": "Deep dive for the 25% weight topic"},
            {"title": "Credit Risk — Malz, Financial Risk Management", "type": "book", "note": "CDS pricing, credit portfolio models, counterparty risk"},
            {"title": "AnalystPrep FRM Question Bank", "type": "practice", "note": "1000+ practice questions with detailed explanations"},
        ],
        "technique": [
            {"title": "Spaced Repetition with Anki", "type": "method", "note": "Create flashcards for formulas and key concepts — research shows 90%+ retention vs. 20% for re-reading"},
            {"title": "Active Recall Practice", "type": "method", "note": "Close the book, write what you remember. Retrieval practice is 2-3x more effective than re-reading (Roediger & Karpicke, 2006)"},
        ],
    },
    "allocq": {
        "frameworks": [
            {"title": "Claude Agent SDK (Anthropic)", "type": "framework", "note": "If building with Claude — native agent loop with tool use"},
            {"title": "LangGraph", "type": "framework", "note": "Graph-based agent orchestration — good for complex multi-agent flows"},
            {"title": "CrewAI", "type": "framework", "note": "Role-based multi-agent — easy to prototype, good for defined agent roles"},
            {"title": "AutoGen (Microsoft)", "type": "framework", "note": "Conversational multi-agent framework — strong for back-and-forth agent collaboration"},
        ],
        "concepts": [
            {"title": "Building Effective Agents (Anthropic)", "type": "guide", "note": "Best practices for agent architecture, tool design, and evaluation"},
            {"title": "Agent evaluation patterns", "type": "concept", "note": "How to test agentic systems — deterministic tests + LLM-as-judge"},
        ],
    },
}


class WorkflowAgent:
    """Orchestrates task management, scheduling, and resources."""

    def __init__(self):
        self.settings = load_settings()

    def get_dashboard_data(self):
        """Return everything the dashboard needs in one call."""
        tasks = load_tasks()
        ranked = rank_tasks(tasks)
        schedule = generate_schedule(ranked, self.settings)
        current = get_current_block(schedule)
        next_block = get_next_block(schedule)
        progress_log = load_progress()

        # Compute progress for each task
        for t in ranked:
            t["progress"] = get_progress(t)

        today_completions = self._today_completions(progress_log)

        return {
            "tasks": ranked,
            "schedule": schedule,
            "current_block": current,
            "next_block": next_block,
            "settings": self.settings,
            "today_completions": today_completions,
        }

    def get_resources(self, task_id):
        """Get curated resources for a task."""
        task = get_task(task_id)
        if not task:
            return None
        category = task.get("category", "general")
        return {
            "task": task["title"],
            "resources": RESOURCES.get(category, {}),
        }

    def get_all_resources(self):
        """Get all resources keyed by category."""
        return RESOURCES

    def toggle_energy_mode(self):
        """Toggle between morning and night_owl mode."""
        self.settings = load_settings()
        current = self.settings.get("energy_mode", "morning")
        new_mode = "night_owl" if current == "morning" else "morning"
        self.settings["energy_mode"] = new_mode
        save_settings(self.settings)
        return new_mode

    def update_settings(self, new_settings):
        self.settings = load_settings()
        self.settings.update(new_settings)
        save_settings(self.settings)
        return self.settings

    def _today_completions(self, progress_log):
        from datetime import date
        today = date.today().isoformat()
        return [p for p in progress_log if p.get("completed_at", "").startswith(today)]
