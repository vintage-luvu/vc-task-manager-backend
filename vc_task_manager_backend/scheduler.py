from datetime import datetime, timedelta
from typing import List, Tuple

from .models import Task


def schedule_tasks(tasks: List[Task], free_slots: List[tuple]):
    # Sort tasks by due date (None -> far future) and priority (lower number = higher priority)
    sorted_tasks = sorted(tasks, key=lambda t: ((t.due_date or datetime.max), t.priority or 0))
    scheduled = []
    for task in sorted_tasks:
        duration = task.duration_minutes or 30
        for i, (start, end) in enumerate(free_slots):
            slot_duration = (end - start).total_seconds() / 60
            if slot_duration >= duration:
                scheduled_start = start
                scheduled_end = start + timedelta(minutes=duration)
                scheduled.append((task, scheduled_start, scheduled_end))
                free_slots[i] = (scheduled_end, end)
                break
    return scheduled
