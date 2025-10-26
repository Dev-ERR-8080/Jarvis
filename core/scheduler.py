# core/scheduler.py
import os
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from utils.notifier import show_notification, show_status_toast
from threading import Lock



REMINDERS_FILE = os.path.join(os.path.dirname(__file__), "..", "reminders.json")
sched = BackgroundScheduler()
sched.start()
_lock = Lock()

def _persist_reminders(reminders_list):
    with _lock:
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(reminders_list, f, indent=2, default=str)

def _load_persisted():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def list_reminders():
    reminders = _load_persisted()
    if not reminders:
        return "No reminders set."

    # Collect only pending reminders
    lines = []
    notif_lines = []
    for idx, r in enumerate(reminders, start=1):
        try:
            run_at_d = datetime.fromisoformat(r['run_at'])
        except Exception:
            continue

        if run_at_d > datetime.now():
            lines.append(f"{idx}. {r['task']} at {r['run_at']}")
            notif_lines.append(f"{idx}. {r['task']} at {run_at_d.strftime('%Y-%m-%d %H:%M')}")

    if not lines:
        return "No pending reminders."

    # Show notification once (not in the loop)
    show_status_toast("Your Reminders", "\n".join(notif_lines), timeout=10)
    # Return plain string (Jarvis-friendly)
    return "\n".join(lines)



def _schedule_job_at(task, run_dt):
    def job_action(t=task):
        show_notification("Reminder", t, timeout=10)
    job = sched.add_job(job_action, 'date', run_date=run_dt)
    return job

def schedule_reminder_at(task, time_str):
    # time_str like "14:30" (24-hour)
    now = datetime.now()
    h, m = map(int, time_str.split(":"))
    run_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
    # if time already passed today, schedule for tomorrow
    if run_dt <= now:
        run_dt += timedelta(days=1)
    job = _schedule_job_at(task, run_dt)
    # persist
    reminders = _load_persisted()
    reminders.append({"task": task, "run_at": str(run_dt)})
    _persist_reminders(reminders)
    return job

def schedule_reminder_in(task, minutes):
    run_dt = datetime.now() + timedelta(minutes=minutes)
    job = _schedule_job_at(task, run_dt)
    reminders = _load_persisted()
    reminders.append({"task": task, "run_at": str(run_dt)})
    _persist_reminders(reminders)
    return job

def load_and_restore():
    items = _load_persisted()
    for it in items:
        try:
            run_dt = datetime.fromisoformat(it["run_at"])
            if run_dt > datetime.now():
                _schedule_job_at(it["task"], run_dt)
        except Exception:
            continue

# Start by restoring persisted reminders
load_and_restore()
