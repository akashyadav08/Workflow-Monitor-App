from datetime import datetime, date


def compute_priority(task):
    """Weighted priority score.

    Score = Urgency*0.30 + Impact*0.30 + DeadlineProximity*0.25 + Dependencies*0.15
    All factors on 1-10 scale.
    """
    urgency = task.get("urgency", 5)
    impact = task.get("impact", 5)
    deps = task.get("dependencies", 3)

    # Deadline proximity: closer deadline → higher score
    deadline_str = task.get("deadline")
    if deadline_str:
        try:
            dl = datetime.fromisoformat(deadline_str).date()
            days_left = (dl - date.today()).days
            if days_left <= 0:
                prox = 10
            elif days_left <= 7:
                prox = 9
            elif days_left <= 14:
                prox = 8
            elif days_left <= 30:
                prox = 7
            elif days_left <= 60:
                prox = 5
            elif days_left <= 120:
                prox = 3
            else:
                prox = 2
        except (ValueError, TypeError):
            prox = 5
    else:
        prox = 5

    score = (urgency * 0.30) + (impact * 0.30) + (prox * 0.25) + (deps * 0.15)
    return round(score, 2)


def rank_tasks(tasks):
    """Return tasks sorted by priority score (highest first)."""
    scored = []
    for t in tasks:
        t["priority_score"] = compute_priority(t)
        scored.append(t)
    scored.sort(key=lambda x: x["priority_score"], reverse=True)
    return scored
