# Workflow Monitor

A two-agent productivity system that combines intelligent task management with science-based motivation. Built as a single-user Flask dashboard with a dark-themed UI.

The system doesn't just track what you need to do — it understands *why* you're stuck and delivers targeted, research-backed interventions to keep you moving.

---

## Architecture

The app runs on a **two-agent model**:

| Agent | Role | Module |
|---|---|---|
| **Workflow Orchestrator** | Tasks, scheduling, resources, progress tracking | `agents/workflow_agent.py` |
| **Motivation Catalyst** | Science-based motivation, nightly reports, daily briefings | `agents/motivation_agent.py` |

Both agents share data through JSON files in the `data/` directory.

### Tech Stack

- **Backend:** Python 3.10+ / Flask 3.0+
- **Frontend:** Vanilla JavaScript, custom CSS (dark theme)
- **Storage:** JSON files (no database required)
- **Dependencies:** Flask only (`pip install flask`)

---

## Quick Start

```bash
cd "Workflow Monitor App"
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5050** in your browser.

---

## Project Structure

```
.
├── app.py                          # Flask application & API routes
├── config.py                       # Settings management
├── requirements.txt                # Dependencies (Flask)
├── agents/
│   ├── workflow_agent.py           # Orchestrator: tasks, schedule, resources
│   └── motivation_agent.py         # Catalyst: motivation, reports, briefings
├── frameworks/
│   ├── priority.py                 # Weighted priority scoring algorithm
│   ├── scheduling.py               # Daily schedule generation (2 modes)
│   ├── motivation_science.py       # 6 science-based motivation frameworks
│   └── nightly_report.py           # 10 PM nightly anchor report engine
├── models/
│   └── task.py                     # Task CRUD, subtask management, progress logging
├── templates/
│   └── index.html                  # Dashboard HTML
├── static/
│   ├── app.js                      # Frontend application logic
│   └── style.css                   # Dark theme styling
└── data/                           # Auto-created JSON storage
    ├── tasks.json                  # Task definitions & state
    ├── settings.json               # User preferences
    ├── progress.json               # Subtask completion audit log
    └── reports.json                # Last 5 nightly reports
```

---

## Features

### 1. Task Management

Full CRUD for tasks and subtasks with rich metadata:

- **Title, description, subtasks** — break work into trackable pieces
- **Deadline** — feeds into priority scoring via deadline proximity
- **Urgency** (1-10) — how time-sensitive the task is
- **Impact** (1-10) — how much completing it matters
- **Cognitive load** (1-10) — how mentally demanding the work is
- **Dependencies** (1-10) — how much other work relies on this
- **Category** — `general`, `job_applications`, `imc_competition`, `frm_exam`, `allocq`
- **Resources** — curated per-category learning materials and links

Subtasks support inline editing, adding, removing, and checkbox completion. Progress is tracked as a percentage (completed subtasks / total subtasks).

### 2. Priority Algorithm

Tasks are ranked by a weighted composite score:

```
Score = Urgency × 0.30 + Impact × 0.30 + DeadlineProximity × 0.25 + Dependencies × 0.15
```

**Deadline proximity mapping:**
| Days Left | Proximity Score |
|---|---|
| Past due | 10 |
| 0-7 days | 9 |
| 8-14 days | 8 |
| 15-30 days | 7 |
| 31-60 days | 5 |
| 61-120 days | 3 |
| 120+ days | 2 |

Tasks are displayed highest-priority first in the dashboard.

### 3. Smart Scheduling

Two energy modes with tailored daily schedules:

**Morning Person Mode:**
- Deep analytical work (IMC, FRM) in the morning when cognitive resources peak
- Creative/building work (AllocQ) in the afternoon
- Lighter tasks (job applications) as warm-up

**Night Owl Mode:**
- Structured warm-up tasks in the morning
- Peak analytical work shifts to afternoon/evening
- Deep creative blocks in late afternoon

Both modes include:
- Fixed family call block (16:00-16:30)
- Scheduled breaks between work blocks
- Lunch break
- End-of-day review block
- Each work block shows the next 3 incomplete subtasks as focus items

Toggle between modes with the header button.

### 4. Science-Based Motivation Engine

Six research-backed frameworks, selected dynamically based on progress level and time of day:

| Framework | Source | When It Activates |
|---|---|---|
| **Temporal Motivation Theory** | Steel, 2007 | Low progress — identifies which variable (expectancy, value, impulsiveness, delay) is bottlenecking motivation |
| **Self-Determination Theory** | Deci & Ryan, 2000 | Mid-progress — feeds autonomy, competence, or relatedness needs |
| **Implementation Intentions** | Gollwitzer, 1999 | Mornings & fresh starts — pre-loads specific if-then action plans |
| **Progress Principle** | Amabile & Kramer, 2011 | Any progress level — makes progress visible and celebrates small wins |
| **Cognitive Behavioral Reframing** | Beck, 1979 | Afternoons & stalls — identifies and counters cognitive distortions |
| **Zeigarnik Effect + Goal Gradient** | Zeigarnik 1927, Hull 1932 | Zero progress or near completion — leverages psychological momentum |

**Task-specific profiles** customize each framework per category:
- **Job Applications:** Counters fortune-telling, emotional reasoning, overgeneralization
- **IMC Competition:** Addresses catastrophizing, comparison, all-or-nothing thinking
- **FRM Exam:** Tackles overwhelm, procrastination rationalization, self-doubt
- **AllocQ:** Counters perfectionism, scope creep, imposter syndrome

The framework selector avoids repeating the same framework consecutively.

### 5. Curated Resources

Per-category learning materials and tools:

- **Job Applications:** Mercor, Seek, LinkedIn strategies; Australian resume format guide; application timing tips
- **IMC Competition:** Orderbook dynamics papers, options pricing textbooks, market-making algorithms, backtesting tools
- **FRM Exam:** Schweser notes, GARP practice exams, Bionic Turtle, spaced repetition methodology
- **AllocQ:** Claude Agent SDK, LangGraph, CrewAI, AutoGen; agent evaluation patterns

### 6. Nightly Anchor Report (10 PM)

Auto-triggers at 10:00 PM every night (also available on-demand). A constructive, forward-looking report designed to be your daily motivational anchor.

**Report sections:**

1. **Summary** — Headline with tone-adaptive styling (gentle / encouraging / strong / celebration) based on daily output
2. **Today's Wins** — Every subtask completed, grouped by task, with overall progress. Zero-completion days receive compassionate messaging grounded in Neff's self-compassion research
3. **Tactical Reframes** — For tasks that didn't see progress: category-specific constructive reframes (no guilt). Each includes a concrete "Tomorrow" action
4. **Tomorrow's Game Plan** — Identifies momentum tasks (ride the goal gradient) and needs-attention tasks (high urgency, low progress). Includes a pre-committed implementation intention for tomorrow morning
5. **Broader Outlook** — Trend analysis across your last 5 saved reports:
   - Completion streak counter
   - Trend detection (upward / steady / dip) with constructive framing
   - Mini bar chart of daily completions
   - Task coverage — which tasks got attention across recent days
   - Consistency note tied to streak length
6. **Anchor Quote** — Tone-matched closing thought to carry into sleep

**Report persistence:**
- Last 5 reports are saved to `data/reports.json`
- Same-day reports replace previous entries (no duplicates)
- "Past Reports" button lets you browse and expand any saved report
- "Wipe All Reports" clears history entirely

### 7. Daily Motivational Briefing

A morning-oriented briefing that generates context-aware motivation for every active task. Shows progress status and a targeted motivational insight per task.

---

## Dashboard Layout

Three-column responsive grid:

| Left Panel | Center Panel | Right Panel |
|---|---|---|
| Today's Schedule | Tasks by Priority | Motivation + Resources |
| Timeline with active block highlighting | Expandable task cards with subtask management | Tab-based: Motivation / Resources |
| Click a block to select its task | Inline subtask editing, adding, removing | Daily Briefing & Nightly Report buttons |

**Footer:** Real-time daily progress stats (subtasks completed today, overall completion rate, active task count).

**Header:** Live clock, current block badge, energy mode toggle.

---

## API Reference

### Dashboard & Tasks

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard` | Full dashboard data (tasks, schedule, current block, settings) |
| `GET` | `/api/tasks` | All tasks ranked by priority |
| `POST` | `/api/tasks` | Create a new task |
| `PUT` | `/api/tasks/<task_id>` | Update a task |
| `DELETE` | `/api/tasks/<task_id>` | Delete a task |

### Subtasks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/tasks/<task_id>/complete/<index>` | Mark subtask complete |
| `POST` | `/api/tasks/<task_id>/uncomplete/<index>` | Unmark subtask |
| `POST` | `/api/tasks/<task_id>/subtasks` | Add a subtask |
| `PUT` | `/api/tasks/<task_id>/subtasks/<index>` | Edit a subtask |
| `DELETE` | `/api/tasks/<task_id>/subtasks/<index>` | Remove a subtask |

### Motivation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/motivation/<task_id>` | Single framework motivation for a task |
| `GET` | `/api/motivation/<task_id>/all` | All 6 frameworks for a task |
| `GET` | `/api/motivation/current` | Motivation for the current schedule block |
| `GET` | `/api/motivation/briefing` | Daily motivational briefing (all tasks) |

### Nightly Reports

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/report/nightly` | Generate tonight's anchor report (auto-saves) |
| `GET` | `/api/report/history` | Retrieve last 5 saved reports |
| `POST` | `/api/report/wipe` | Delete all saved reports |

### Resources & Settings

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/resources/<task_id>` | Curated resources for a task |
| `GET` | `/api/resources` | All resources by category |
| `GET` | `/api/settings` | Current settings |
| `POST` | `/api/settings` | Update settings |
| `POST` | `/api/settings/toggle-mode` | Toggle morning / night owl mode |

---

## Data Storage

All data lives in the `data/` directory as JSON files:

| File | Purpose | Behavior |
|---|---|---|
| `tasks.json` | Task definitions, subtasks, completion state | Read/write on every task operation |
| `settings.json` | Energy mode, work hours, break durations | Merged with defaults on load |
| `progress.json` | Append-only audit log of subtask completions | Timestamped entries for tracking daily output |
| `reports.json` | Last 5 nightly anchor reports | Auto-pruned to 5; same-day entries replaced |

---

## Configuration

Default settings (customizable via the API or `data/settings.json`):

```json
{
  "energy_mode": "morning",
  "work_start": "09:30",
  "work_end": "20:00",
  "family_call": {"start": "16:00", "end": "16:30"},
  "break_duration_minutes": 15,
  "lunch_duration_minutes": 60,
  "deep_work_block_minutes": 120,
  "review_block_minutes": 15
}
```

---

## Research Foundations

The motivation system draws from peer-reviewed behavioral science:

- **Temporal Motivation Theory** — Steel, P. (2007). The nature of procrastination.
- **Self-Determination Theory** — Deci, E.L. & Ryan, R.M. (2000). Intrinsic motivation and self-determination.
- **Implementation Intentions** — Gollwitzer, P.M. (1999). Implementation intentions: Strong effects of simple plans.
- **Progress Principle** — Amabile, T. & Kramer, S. (2011). The progress principle.
- **Cognitive Behavioral Therapy** — Beck, A.T. (1979). Cognitive therapy and the emotional disorders.
- **Zeigarnik Effect** — Zeigarnik, B. (1927). On finished and unfinished tasks.
- **Goal Gradient Effect** — Hull, C.L. (1932). The goal gradient hypothesis.
- **Self-Compassion** — Neff, K.D. (2003). Self-compassion: An alternative conceptualization of a healthy attitude toward oneself.
- **Habit Formation** — Lally, P. et al. (2009). How are habits formed.
- **Deliberate Practice** — Ericsson, K.A. (1993). The role of deliberate practice.
