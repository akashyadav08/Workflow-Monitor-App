"""Science-based motivation engine.

Implements six frameworks from behavioral science and psychology:
1. Temporal Motivation Theory (Steel, 2007)
2. Self-Determination Theory (Deci & Ryan, 2000)
3. Implementation Intentions (Gollwitzer, 1999)
4. Progress Principle (Amabile & Kramer, 2011)
5. Cognitive Behavioral Reframing
6. Zeigarnik Effect + Goal Gradient
"""

import random
from datetime import datetime


# ── Task-specific motivation profiles ──────────────────────────────────────────

TASK_PROFILES = {
    "job_applications": {
        "tmt_weak_link": "expectancy",
        "cognitive_distortions": [
            {
                "distortion": "Fortune-telling: 'Nobody will respond'",
                "reframe": "Each application is an independent probability event. At a 3-5% response rate, 30 applications statistically yields 1-2 interviews. You're not predicting the future — you're playing the odds. Keep the funnel full.",
            },
            {
                "distortion": "Emotional reasoning: 'Applying feels pointless so it must be'",
                "reframe": "Feelings are data about your current state, not about reality. The job market in Australia is active for quantitative and tech roles. Feeling discouraged after rejections is normal — it's your brain's loss aversion, not a signal about your employability.",
            },
            {
                "distortion": "Overgeneralization: 'I didn't hear back from those, so I won't from any'",
                "reframe": "Each company has different needs, timelines, and filters. A non-response from Company A tells you zero about Company B. Treat each application as a fresh trial.",
            },
        ],
        "implementation_intentions": [
            "When I sit down at {time}, I will open {platform} and search for 3 roles matching my skills before doing anything else.",
            "When I feel the urge to skip today's applications, I will commit to just opening one job listing and reading the requirements.",
            "When I finish an application, I will immediately log it in my tracker before context-switching.",
        ],
        "sdt_autonomy": [
            "Which platform feels most promising today — Mercor, Seek, or LinkedIn? Start where your energy pulls you.",
            "You could focus on quality (2-3 highly tailored applications) or quantity (5-6 standard applications) today. Which matches your energy?",
        ],
        "sdt_competence": [
            "Each application you tailor is a rep at a real skill — communicating your value under constraints. You're getting measurably better at this.",
            "Track your response rate over time. Even a 1% improvement in callback rate from better cover letters compounds across hundreds of applications.",
        ],
        "sdt_relatedness": [
            "Connect with people already working at target companies on LinkedIn. A warm referral increases interview odds by 5-10x compared to cold applications.",
            "You're not just job hunting — you're building a network in the Australian market that compounds regardless of any single application outcome.",
        ],
    },
    "imc_competition": {
        "tmt_weak_link": "delay",
        "cognitive_distortions": [
            {
                "distortion": "Catastrophizing: 'There's too much to learn in a month'",
                "reframe": "You don't need to master all of quantitative finance. IMC Prosperity tests 5-6 specific problem types. Last year you completed 3 rounds — you already have the foundation. This year is about sharpening specific edges, not starting from zero.",
            },
            {
                "distortion": "Comparison: 'Other teams are way more prepared'",
                "reframe": "Competitions reward problem-solving under constraints, not encyclopedic knowledge. Your unique combination of skills IS your competitive advantage. Focus on developing your strongest strategies rather than trying to cover everything.",
            },
            {
                "distortion": "All-or-nothing: 'If I can't win, why bother?'",
                "reframe": "The ROI of competition prep is in the skills you build, not just the ranking. Orderbook analysis, options pricing intuition, and algorithmic thinking are directly transferable to your career. Every hour of prep has value regardless of final placement.",
            },
        ],
        "implementation_intentions": [
            "When I start my IMC study block, I will spend the first 10 minutes reviewing yesterday's notes before tackling new material.",
            "When I feel overwhelmed by theory, I will switch to coding a simple implementation of the concept — hands-on learning breaks the paralysis.",
            "When I finish studying a concept, I will write one practice problem for myself to test understanding tomorrow (spaced retrieval).",
        ],
        "sdt_autonomy": [
            "What aspect of trading pulls your curiosity most right now — orderbook dynamics, options Greeks, or market-making algorithms? Follow the energy.",
            "You could go theory-first (read then implement) or code-first (build then understand why). Pick whichever feels more natural today.",
        ],
        "sdt_competence": [
            "You attempted Prosperity 3 — that means you've already seen the competition format, understand the platform, and know what to expect. That's a real advantage over first-time participants.",
            "Try solving one of last year's challenges with your current knowledge. You'll likely surprise yourself with how much you already know.",
        ],
        "sdt_relatedness": [
            "The IMC Prosperity community on Discord and Reddit shares strategies from past rounds. Engaging with that community both teaches you and keeps you motivated.",
            "Many quant firms watch IMC Prosperity results for talent. Your preparation here is visible to the exact industry you want to enter.",
        ],
    },
    "frm_exam": {
        "tmt_weak_link": "delay",
        "cognitive_distortions": [
            {
                "distortion": "Overwhelm: 'The material is massive and I can't retain it all'",
                "reframe": "FRM L2 has a ~50% pass rate. You don't need perfection — you need consistent competence across topics. Spaced repetition research shows that 30 minutes of active recall daily beats 3-hour cramming sessions for long-term retention. Work with your memory, not against it.",
            },
            {
                "distortion": "Procrastination rationalization: 'I have until August, I can start later'",
                "reframe": "Spaced repetition is most effective with longer intervals between study sessions. Starting now with 1.5 hours daily means August-you has seen every topic 4-5 times. Starting in June means cramming with 1-2 passes. The math favors starting now.",
            },
            {
                "distortion": "Self-doubt: 'I might fail anyway'",
                "reframe": "The base rate is in your favor — 50% pass. With structured preparation and active recall, you're selecting yourself into the prepared half. The exam tests breadth of competence, not depth of genius.",
            },
        ],
        "implementation_intentions": [
            "When my FRM study block starts, I will do 10 minutes of flashcard review (active recall) before reading new material.",
            "When I encounter a concept I don't understand, I will explain it out loud in simple terms (Feynman technique) before moving on.",
            "When I finish a study session, I will write down 3 key takeaways without looking at notes (retrieval practice).",
        ],
        "sdt_autonomy": [
            "Which FRM topic interests you most today? Starting with genuine curiosity makes the rest flow more easily.",
            "Practice questions or concept review — which do you feel you need more of right now? Trust your own judgment on what's working.",
        ],
        "sdt_competence": [
            "Each practice question you attempt — right or wrong — strengthens the neural pathway. Wrong answers with immediate review are actually MORE effective for learning than easy correct answers.",
            "Track your accuracy on practice questions weekly. Watching the trend line rise is one of the most reliable motivators research has found.",
        ],
        "sdt_relatedness": [
            "FRM certification signals risk management competence to every financial institution globally. Each study hour is building a credential that opens doors for years.",
            "Many FRM candidates study in online groups. Consider Bionic Turtle forums or AnalystPrep communities — shared struggle builds commitment.",
        ],
    },
    "allocq": {
        "tmt_weak_link": "impulsiveness",
        "cognitive_distortions": [
            {
                "distortion": "Perfectionism: 'The architecture isn't clean enough yet'",
                "reframe": "A working prototype you can test and iterate on beats a theoretically perfect design that never ships. The best architecture emerges from building, not planning. Ship the ugly version first.",
            },
            {
                "distortion": "Scope creep: 'I should also add this feature...'",
                "reframe": "Every feature you add before validating the core doubles your debugging surface. Constrain scope ruthlessly. The testing base needs to work, not impress.",
            },
            {
                "distortion": "Imposter syndrome: 'Am I even capable of building an agentic system?'",
                "reframe": "You're literally building a multi-agent workflow system right now (this app). Agentic systems are just programs with loops, tools, and decision points. You already have the building blocks.",
            },
        ],
        "implementation_intentions": [
            "When I start my AllocQ block, I will define ONE specific goal for this session before writing any code.",
            "When I feel tempted to add scope, I will write the idea in a 'later' list and return to the current task.",
            "When I get stuck on architecture, I will build the simplest possible version that works, then refactor.",
        ],
        "sdt_autonomy": [
            "What's the smallest testable piece of AllocQ you could build today? Start there.",
            "You have full creative control over this architecture. What excites you most about building it?",
        ],
        "sdt_competence": [
            "Building an agentic team is a high-signal portfolio piece. Every component you complete is demonstrable expertise in AI engineering.",
            "Each integration test that passes validates your design decisions. Let the green checkmarks compound.",
        ],
        "sdt_relatedness": [
            "AllocQ with an agentic backend would be a genuinely useful product. You're building something people can use.",
            "The agentic AI space is moving fast. Building hands-on experience now positions you ahead of most engineers.",
        ],
    },
}


# ── Motivation Engine ──────────────────────────────────────────────────────────

class MotivationEngine:
    """Generates context-aware, science-based motivation."""

    def __init__(self):
        self._last_framework = None
        self._frameworks = [
            "tmt", "sdt", "implementation_intentions",
            "progress_principle", "cbt_reframe", "zeigarnik_goal_gradient",
        ]

    def get_motivation(self, task, progress_pct, time_of_day=None, force_framework=None):
        """Generate motivation for a specific task and context.

        Args:
            task: Task dict with category, title, subtasks, etc.
            progress_pct: Float 0.0-1.0 of subtask completion
            time_of_day: "morning", "midday", "afternoon", "evening" (auto-detected if None)
            force_framework: Force a specific framework (optional)

        Returns:
            dict with framework, title, message, principle, action
        """
        if time_of_day is None:
            time_of_day = self._detect_time_of_day()

        category = task.get("category", "general")
        profile = TASK_PROFILES.get(category)

        if force_framework:
            framework = force_framework
        else:
            framework = self._select_framework(progress_pct, time_of_day)

        self._last_framework = framework

        if not profile:
            return self._generic_motivation(task, progress_pct, framework)

        method = getattr(self, f"_apply_{framework}", None)
        if method:
            return method(task, profile, progress_pct, time_of_day)
        return self._generic_motivation(task, progress_pct, framework)

    def get_all_motivations(self, task, progress_pct):
        """Get motivation from every framework for a task."""
        results = []
        for fw in self._frameworks:
            results.append(self.get_motivation(task, progress_pct, force_framework=fw))
        return results

    def _detect_time_of_day(self):
        hour = datetime.now().hour
        if hour < 12:
            return "morning"
        elif hour < 14:
            return "midday"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"

    def _select_framework(self, progress_pct, time_of_day):
        """Context-aware framework selection."""
        # Progress-based selection
        if progress_pct == 0:
            candidates = ["zeigarnik_goal_gradient", "implementation_intentions"]
        elif progress_pct < 0.3:
            candidates = ["tmt", "implementation_intentions", "sdt"]
        elif progress_pct < 0.7:
            candidates = ["sdt", "progress_principle", "cbt_reframe"]
        elif progress_pct < 0.9:
            candidates = ["progress_principle", "zeigarnik_goal_gradient"]
        else:
            candidates = ["progress_principle", "zeigarnik_goal_gradient"]

        # Time-based adjustments
        if time_of_day == "morning":
            candidates.append("implementation_intentions")
        elif time_of_day == "afternoon":
            candidates.append("cbt_reframe")
        elif time_of_day == "evening":
            candidates.append("progress_principle")

        # Avoid repeating the same framework
        if self._last_framework in candidates and len(candidates) > 1:
            candidates.remove(self._last_framework)

        return random.choice(candidates)

    # ── Framework implementations ──────────────────────────────────────────

    def _apply_tmt(self, task, profile, progress_pct, time_of_day):
        """Temporal Motivation Theory: M = (E × V) / (I × D)"""
        weak = profile.get("tmt_weak_link", "expectancy")
        interventions = {
            "expectancy": {
                "title": "Build Expectancy (Temporal Motivation Theory)",
                "message": f"Your motivation equation is bottlenecked by self-belief on '{task['title']}'. Research shows the fastest fix is a micro-win: pick the smallest possible subtask and finish it. Success on even a trivial task raises your brain's expectancy estimate for the larger goal.",
                "principle": "Steel's TMT (2007): Motivation = (Expectancy × Value) / (Impulsiveness × Delay). Low expectancy kills motivation faster than any other factor.",
                "action": "Pick the single easiest incomplete subtask and finish it in the next 10 minutes. One completion rewires your expectancy upward.",
            },
            "value": {
                "title": "Reconnect to Value (Temporal Motivation Theory)",
                "message": f"The 'why' behind '{task['title']}' may feel distant right now. Reconnect: what specific outcome does completing this unlock for your career? Write it down in one sentence. Research shows externalizing your purpose reactivates value-driven motivation.",
                "principle": "TMT: When value perception drops, reconnecting task to identity and long-term goals restores the numerator of the motivation equation.",
                "action": "Write one sentence: 'Completing this task matters because ___.' Be specific about the outcome, not abstract about importance.",
            },
            "impulsiveness": {
                "title": "Reduce Impulsiveness (Temporal Motivation Theory)",
                "message": f"Distractions are winning right now. That's not a character flaw — it's the impulsiveness variable in the motivation equation overpowering value. The fix isn't willpower (that's depletable), it's environment design.",
                "principle": "TMT: High impulsiveness in the denominator divides away motivation regardless of how important the task is. Environment design > willpower.",
                "action": "Phone on airplane mode. Close all non-essential tabs. Set a 25-minute timer. Make starting the path of least resistance.",
            },
            "delay": {
                "title": "Shorten the Delay (Temporal Motivation Theory)",
                "message": f"The deadline for '{task['title']}' feels far away, so your brain discounts its value (hyperbolic discounting). Create an artificial proximal deadline: what can you finish TODAY that constitutes real progress?",
                "principle": "TMT: Humans hyperbolically discount future rewards. A goal 30 days away feels ~70% less motivating than one due tomorrow. Proximal sub-deadlines counteract this.",
                "action": "Set a goal for what 'done' looks like by end of today. Make it specific and completable.",
            },
        }
        return {"framework": "Temporal Motivation Theory", **interventions[weak]}

    def _apply_sdt(self, task, profile, progress_pct, time_of_day):
        """Self-Determination Theory: Autonomy, Competence, Relatedness."""
        # Select the most relevant need based on context
        if progress_pct < 0.3:
            need = "autonomy"  # Early on, choice builds ownership
        elif progress_pct < 0.7:
            need = "competence"  # Mid-way, competence feedback sustains
        else:
            need = "relatedness"  # Near end, purpose and connection push through

        messages = profile.get(f"sdt_{need}", [])
        msg = random.choice(messages) if messages else f"Trust your capacity on '{task['title']}'."

        need_labels = {
            "autonomy": ("Autonomy", "Deci & Ryan (2000): Autonomy — the sense of choice and volition — is the strongest predictor of intrinsic motivation. Feeling controlled kills engagement; feeling ownership sustains it."),
            "competence": ("Competence", "SDT: Competence need — optimal challenge that stretches ability without overwhelming. When met, it produces flow states and intrinsic motivation that outperform any external reward."),
            "relatedness": ("Relatedness", "SDT: Relatedness — connection to others and to purpose beyond self. Knowing your work matters to someone or something sustains effort through difficult stretches."),
        }

        label, principle = need_labels[need]
        return {
            "framework": "Self-Determination Theory",
            "title": f"Feed Your {label} Need",
            "message": msg,
            "principle": principle,
            "action": self._sdt_action(need, task),
        }

    def _sdt_action(self, need, task):
        actions = {
            "autonomy": f"Before starting '{task['title']}', choose ONE thing: which subtask, which approach, or which resource. Making one deliberate choice activates ownership.",
            "competence": "After completing your next subtask, rate the difficulty 1-5. If it's consistently 1-2, increase challenge. If 4-5, break it into smaller pieces. Stay in the 3 zone.",
            "relatedness": "Think of one person who would benefit from or be impressed by your progress on this. Hold that image while you work.",
        }
        return actions.get(need, "Take one deliberate step forward.")

    def _apply_implementation_intentions(self, task, profile, progress_pct, time_of_day):
        """Implementation Intentions: specific if-then plans."""
        intentions = profile.get("implementation_intentions", [])
        intention = random.choice(intentions) if intentions else f"When I start '{task['title']}', I will focus on the first incomplete subtask."

        # Fill in time placeholder
        now = datetime.now()
        intention = intention.replace("{time}", now.strftime("%I:%M %p"))

        # Fill in platform placeholder for jobs
        if task.get("category") == "job_applications":
            platforms = ["Mercor", "Seek", "LinkedIn"]
            intention = intention.replace("{platform}", random.choice(platforms))

        return {
            "framework": "Implementation Intentions",
            "title": "Set Your If-Then Plan (Gollwitzer)",
            "message": intention,
            "principle": "Gollwitzer (1999): Implementation intentions ('When X, I will Y') double to triple follow-through rates in meta-analyses. They work by pre-loading the decision, so when the cue arrives, action is automatic rather than deliberated.",
            "action": "Say the intention out loud or write it down. The act of explicit commitment activates the automaticity effect.",
        }

    def _apply_progress_principle(self, task, profile, progress_pct, time_of_day):
        """Progress Principle: making progress visible."""
        completed = len(task.get("completed_subtasks", []))
        total = len(task.get("subtasks", []))

        if progress_pct == 0:
            msg = f"You haven't started on subtasks for '{task['title']}' yet. Research shows that completing even ONE small item creates disproportionate motivation — the brain registers 'I'm the kind of person who makes progress on this' and momentum follows."
            action = "Complete just one subtask. Not two. Not three. One. Then notice how you feel."
        elif progress_pct < 0.5:
            msg = f"You've completed {completed} of {total} subtasks on '{task['title']}'. You're building momentum. Amabile's research on 12,000 diary entries found that making progress on meaningful work is the #1 driver of positive inner work life — above recognition, incentives, or interpersonal support."
            action = "Before moving on, take 10 seconds to acknowledge what you just completed. Conscious recognition of progress amplifies its motivational effect."
        elif progress_pct < 0.9:
            pct = int(progress_pct * 100)
            msg = f"{pct}% complete on '{task['title']}'. You're past the halfway point — this is where the goal gradient effect kicks in. Research shows people naturally accelerate as they approach completion. You're in the acceleration zone."
            action = f"You have {total - completed} subtasks remaining. Can you finish one more before your next break? Ride the gradient."
        else:
            msg = f"You're at {int(progress_pct * 100)}% on '{task['title']}' — almost done. The finish line effect is real: marathon runners speed up in the last mile, loyalty card members buy more frequently near the reward. Channel that energy."
            action = "Push through to completion. The satisfaction of finishing compounds — it raises your baseline motivation for the NEXT task."

        return {
            "framework": "Progress Principle",
            "title": "Your Progress Is Your Fuel",
            "message": msg,
            "principle": "Amabile & Kramer (2011): Across 12,000+ diary entries from 238 professionals, progress on meaningful work was the strongest predictor of positive emotions, motivation, and favorable perceptions. Small wins > big events.",
            "action": action,
        }

    def _apply_cbt_reframe(self, task, profile, progress_pct, time_of_day):
        """Cognitive Behavioral Reframing."""
        distortions = profile.get("cognitive_distortions", [])
        if not distortions:
            return self._generic_motivation(task, progress_pct, "cbt_reframe")

        item = random.choice(distortions)
        return {
            "framework": "Cognitive Behavioral Reframing",
            "title": "Check Your Thinking",
            "message": f"**Common thought pattern:** {item['distortion']}\n\n**Reality check:** {item['reframe']}",
            "principle": "Beck's CBT (1979): Cognitive distortions — systematic errors in thinking — directly suppress motivation by making tasks seem harder, less rewarding, or more futile than they actually are. Identifying and reframing them restores accurate self-assessment.",
            "action": "If this distortion resonated, write down the automatic thought you had, then write the reframe next to it. Externalizing breaks the loop.",
        }

    def _apply_zeigarnik_goal_gradient(self, task, profile, progress_pct, time_of_day):
        """Zeigarnik Effect + Goal Gradient."""
        if progress_pct == 0:
            # Zeigarnik: starting creates cognitive tension that pulls toward completion
            return {
                "framework": "Zeigarnik Effect",
                "title": "Just Start — Your Brain Will Do the Rest",
                "message": f"Commit to working on '{task['title']}' for exactly 5 minutes. Not 25, not 60 — just 5. The Zeigarnik effect means that once you start a task, your brain creates an open loop that generates its own pull toward completion. The hardest part is literally the first minute.",
                "principle": "Bluma Zeigarnik (1927): Incomplete tasks occupy mental resources and create intrinsic motivation to complete them. The effect activates the moment you begin, not when you plan to begin. Starting > planning.",
                "action": "Set a 5-minute timer. Open the first subtask. Begin. You can stop after 5 minutes with zero guilt — but research predicts you won't want to.",
            }
        else:
            # Goal gradient: accelerate toward completion
            completed = len(task.get("completed_subtasks", []))
            total = len(task.get("subtasks", []))
            remaining = total - completed
            return {
                "framework": "Goal Gradient Effect",
                "title": f"{remaining} Steps to Go — You're Accelerating",
                "message": f"You've completed {completed}/{total} subtasks. The goal gradient hypothesis (Hull, 1932) predicts that effort naturally intensifies as the goal gets closer. This isn't motivational fluff — it's been replicated in everything from rats in mazes to customers with loyalty cards to marathon runners. You are neurologically wired to push harder now.",
                "principle": "Hull (1932), Kivetz et al. (2006): The goal gradient effect — effort and motivation increase with proximity to the goal. This is driven by dopaminergic reward anticipation that intensifies as the expected reward gets closer.",
                "action": f"Focus on the gap: {remaining} subtasks. Can you close one in the next 15 minutes? Each completion makes the next one feel more urgent and satisfying.",
            }

    def _generic_motivation(self, task, progress_pct, framework):
        return {
            "framework": framework.replace("_", " ").title(),
            "title": "Keep Moving Forward",
            "message": f"You're working on '{task['title']}'. Every session builds capability that compounds. Focus on the process, not the outcome.",
            "principle": "Deliberate practice research (Ericsson, 1993): Focused effort with feedback produces expertise. The key is consistency and engagement quality, not raw hours.",
            "action": "Identify the ONE thing that would move this task forward most. Do that next.",
        }
