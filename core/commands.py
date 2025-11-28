# core/commands.py
import subprocess
import datetime
import difflib
import os
import re
from openai import audio
import spacy
import wikipedia
from winotify import Notification
from services.calendar_service import add_events_to_calendar
from services.email_processor import extract_events_from_emails
from utils.screen_interaction import ScreenInteraction
from services.email_service import send_email_cmd, send_formatted_email_cmd
from utils import system_actions, notifier
from core import scheduler
import threading
from win10toast_click import ToastNotifier

toaster = ToastNotifier()

def _close_match(word, possibilities, cutoff=0.7):
    matches = difflib.get_close_matches(word, possibilities, n=1, cutoff=cutoff)
    return matches[0] if matches else None

def get_time():
    return f"The time is {datetime.datetime.now().strftime('%H:%M:%S')}"

def get_date():
    return f"Today's date is {datetime.date.today().strftime('%B %d, %Y')}"

def open_app_cmd(app_name):
    return system_actions.open_app(app_name)

def search_cmd(query):
    system_actions.search_web(query)
    return f"Searching for {query}"

def play_cmd(query):
    system_actions.play_youtube(query)
    return f"Playing {query} on YouTube"

def weather_cmd(location=None):
    try:
        data = system_actions.get_weather(location)
        if isinstance(data, str):
            return data
        # data contains a dict with weather info
        return f"Weather in {data['name']}: {data['weather_desc']}, temperature {data['temp_c']}°C"
    except Exception as e:
        return f"Could not fetch weather: {e}"

def screenshot_cmd():
    try:
        result = system_actions.take_screenshot()
        return result
    except Exception as e:
        return f"Could not take screenshot: {e}"

def set_brightness_cmd(command_text):
    m = re.search(r"(\d{1,3})", command_text)
    if m:
        level = int(m.group(1))
        if 0 <= level <= 100:
            return system_actions.set_brightness(level)
        else:
            return "Brightness level must be between 0 and 100."
    return "Could not parse brightness level. Please say: 'Set brightness to N' where N is between 0 and 100."
    # return system_actions.set_brightness(100)

def toggle_airplane_mode_cmd():
    try:
        result = system_actions.toggle_airplane_mode()
        return result
    except Exception as e:
        return f"Could not toggle Airplane Mode: {e}"
    
def sys_stats_cmd():
    cpu, mem = system_actions.get_system_stats()
    return f"CPU usage: {cpu}% | RAM usage: {mem}%"

def get_battery_cmd():
    try:
        battery = system_actions.get_battery_status()
        return battery
    except Exception as e:
        return f"Could not get battery status: {e}"

def set_reminder_cmd(command_text):
    """
    Expected forms:
      - remind me to <task> at HH:MM
      - remind me to <task> in N minutes
      - list reminders
    """
    # try "remind me to X at HH:MM"
    m_at = re.search(r"remind me to (.+?) at (\d{1,2}:\d{2})", command_text, re.I)
    if m_at:
        task = m_at.group(1).strip()
        time_str = m_at.group(2).strip()
        job = scheduler.schedule_reminder_at(task, time_str)
        return f"Reminder set for {time_str}: {task}"

    m_in = re.search(r"remind me to (.+?) in (\d+)\s*minutes?", command_text, re.I)
    if m_in:
        task = m_in.group(1).strip()
        minutes = int(m_in.group(2))
        job = scheduler.schedule_reminder_in(task, minutes)
        return f"Reminder set in {minutes} minutes: {task}"

    
    return "Could not parse reminder. Please say: 'Remind me to <task> at HH:MM' or 'Remind me to <task> in N minutes'."
    
def list_reminders(command_text):    
    ls_rm = re.search(r"list reminders", command_text, re.I)
    if ls_rm:
        return scheduler.list_reminders()
    
def sys_action_cmd(action):
   system_actions.run_actions(action)
   return f"Running system command: {action}"

def wiki_cmd(query):
    try:
        q = query.replace("who is", "").replace("what is", "").strip()
        summary = wikipedia.summary(q, sentences=2, auto_suggest=True, redirect=True)
        return summary
    except Exception as e:
        return f"Could not find summary: {e}"
    
# def send_email_cmd(to_email, subject, body):
#     """Wrapper for sending email as a command."""
#     print(f"Sending email to {to_email}...")
#     response = send_email_cmd(to_email, subject, body)
#     return response

def process_and_add_events_cmd():
    """
    Combines email processing and calendar integration.
    """
    events = extract_events_from_emails()
    #print("Extracted events from email sending to add the event to calendar")
    if isinstance(events, str):  
        return events
    
    if not events:
        return "No new events found in unread emails."
        
    # voice_output.speak(f"Found {len(events)} new events. Adding them to your calendar now.")
    #print("response from calendar is:")
    response = add_events_to_calendar(events)
    return response

def run_background_task(command, title="Jarvis Task", message="Running in background..."):
    """
    Runs a given command as a background thread and shows a toast notification.
    """
    def task():
        notifier.show_status_toast(title, f"{message}", duration=5, threaded=True)
        try:
            subprocess.run(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
            notifier.show_status_toast(title, "✅ Task completed successfully.", duration=5, threaded=True)
        except Exception as e:
            notifier.show_status_toast(title, f"❌ Task failed: {e}", duration=5, threaded=True)

    thread = threading.Thread(target=task, daemon=True)
    thread.start()

nlp=spacy.load("en_core_web_sm")

def handle_command(command: str ):
    doc = nlp(command.strip().lower())
    c = command.strip().lower()
    action = None
    time = None
    
    # 1. Intent Check (Already updated)
    if any(token.lemma_ in ["remind", "reminder", "remember"] for token in doc):
        
        # --- Time/Duration Extraction (Your updated logic) ---
        
        # A. First, try to extract a formal Time/Duration entity (e.g., "10 minutes", "tomorrow")
        for ent in doc.ents:
            # Added 'CARDINAL' check for isolated numbers that *are* part of a larger time entity
            if ent.label_ in ["TIME", "DATE", "DURATION", "CARDINAL"]:
                # Only use CARDINAL if it looks like a time (e.g., not just 'a' or 'one')
                if ent.label_ == "CARDINAL" and ent.text in ["a", "one", "some", "the"]:
                    continue
                time = ent.text
                break
        
        # B. If no formal time entity is found, look for an isolated number near a time preposition
        if not time:
            for token in doc:
                if token.pos_ == "NUM" or token.text.isdigit():
                    if token.i > 0:
                        prev_token = doc[token.i - 1]
                        if prev_token.lemma_ in ["after", "in", "for"]: 
                            # Case: "at 10 am"
                            if token.i < len(doc) - 1 and doc[token.i + 1].lemma_ in ["o'clock", "am", "pm"]:
                                time = token.text + " " + doc[token.i + 1].text
                                break
                            
                            # Case: "after 10" -> Infer "minutes"
                            elif prev_token.lemma_ in ["after", "in", "for"]:
                                time = token.text + " minutes"
                                break

        # --- Action Extraction (The Missing Logic) ---
        
        # Strategy 1: Dependency Parsing (Best for "remind me to X")
        # Look for the main verb and its dependent clauses, usually after "to" or "that".
        for token in doc:
            # Target the main verbs that trigger the reminder (e.g., 'remind', 'set')
            if token.lemma_ in ["remind", "set", "tell"]:
                # Look for the complement (what the user is being reminded *to do*)
                for child in token.children:
                    # Common dependencies for the main action are xcomp (open clausal complement) or ccomp (clausal complement)
                    if child.dep_ in ["xcomp", "ccomp"]:
                        action = "".join([t.text_with_ws for t in child.subtree]).strip()
                        break
                if action:
                    break
            
            # Look for the action directly after 'reminder to'
            if token.lemma_ == "reminder" and token.i < len(doc) - 1 and doc[token.i + 1].lemma_ == "to":
                # Find the start of the action phrase (after 'to')
                start_index = token.i + 2
                
                # Exclude the time phrase from the action
                action_tokens = []
                for t in doc[start_index:]:
                    # Stop if we hit a known time preposition or a common filler
                    if t.lemma_ in ["after", "in", "for", "at"]:
                        break
                    # Ensure we don't include the time value itself
                    if time and t.text in time.split():
                        break
                    
                    action_tokens.append(t.text)
                
                action = " ".join(action_tokens).strip()
                if action:
                    break

        # Strategy 2: Fallback Token Filtering (Simple, less accurate but catches many cases)
        if not action:
            # Collect all Nouns, Proper Nouns, and Verbs that aren't the command keywords
            relevant_tokens = []
            
            # Keywords to ignore (we know these are part of the command structure)
            ignore_lemmas = {"remind", "reminder", "remember", "me", "after", "in", "to", "for", "set", "a", "my"}
            
            for token in doc:
                # Exclude time-related tokens that might have been inferred
                if time and token.text in time.split():
                    continue
                
                if token.lemma_ not in ignore_lemmas and token.pos_ in ["VERB", "NOUN", "PROPN"]:
                    relevant_tokens.append(token.text)
            
            if relevant_tokens:
                # Use the relevant tokens as the action, simple but effective
                action = " ".join(relevant_tokens).strip()

        # --- Action Execution ---
        
        # Filter out "drink" if the action is just "drink" and the time is set 
        # (Assuming the "drink water" is the primary goal)
        if action == "drink" and time:  
            action = "drink water"
            
        if action and time:
            # This is where you call your actual scheduler function: set_reminder_cmd(action, time)
            
            return f"Reminder set for: '{action}' in {time}"
        elif action:
            return f"Reminder set for: '{action}' - please specify the time."
        elif time:
            return f"Reminder time: {time} - but what should I remind you about?"
        else:
            return "I need more information to set a reminder. Please specify what and when."

    
    # Placement drive automation
    if any(kw in command for kw in [
        "placement drive", "placement portal", "update placements notion", "check jobs", "summarize drives"
    ]):
        try:
            base_path = os.path.dirname(__file__)
            scraper_path = os.path.join(base_path, "live_scraper.py")

            cmd = [
                "python",
                scraper_path,
                "--mode", "attach",
                "--drives-url", "https://ums.lpu.in/Placements/HomePlacementStudent.aspx"
            ]

            run_background_task(
                cmd,
                title="Placement Automation",
                message="Summarizing latest placement drives and updating Notion..."
            )

            return "I'm checking the latest placement drives and updating your Notion page in the background."

        except Exception as e:
            return f"❌ Failed to start placement automation: {e}"
    
    # Check for events from emails
    if "check for events" in c or "process my unread emails" in c:
        return run_background_task(
            process_and_add_events_cmd,
            title="Email Event Extraction",
            message="Processing unread emails to extract events..."
        )
        # return process_and_add_events_cmd()
        
    # Quit
    if c in ("exit", "quit", "bye"):
        return "Goodbye!"

    # Open app
    if c.startswith("open "):
        app = c.split("open ", 1)[1].strip()
        return open_app_cmd(app)

    # Search
    if c.startswith("search "):
        q = command.split("search ", 1)[1].strip()
        return search_cmd(q)

    # Play
    if c.startswith("play "):
        q = command.split("play ", 1)[1].strip()
        return play_cmd(q)

    # Weather
    if "weather" in c:
        # try to extract location after 'in'
        m = re.search(r"weather(?: in)? (.+)", command, re.I)
        loc = m.group(1).strip() if m else None
        return weather_cmd(loc)

    # System stats
    if "cpu" in c or "ram" in c or "system status" in c or "system stats" in c:
        return sys_stats_cmd()

    # Reminder
    # if "remind me" in c:
    #     return set_reminder_cmd(command)
    
    if "list reminders" in c:
        return scheduler.list_reminders()

    # Wikipedia quick queries
    if c.startswith("who is ") or c.startswith("what is ") or c.startswith("tell me about "):
        return wiki_cmd(command)

    # System actions
    sys_actions = ["shutdown", "restart", "log off", "lock"]
    for action in sys_actions:
        if action in c:
            return sys_action_cmd(action)

    if "screenshot" in c or "screen shot" in c or "capture screen" in c:
        return screenshot_cmd()
    
    if "battery" in c or "battery status" in c or "battery percentage" in c:
        return get_battery_cmd()
    
    if "set brightness to" in c or "set screen brightness to" in c or "adjust brightness to" in c or "change brightness to" in c or "brightness" in c:
        return set_brightness_cmd(c)
    
    if "airplane mode" in c or "flight mode" in c or "toggle airplane mode" in c or "toggle flight mode" in c or "turn on airplane mode" in c or "turn off airplane mode" in c:
        return toggle_airplane_mode_cmd()
    
    if "send email" in command:
    # Example pattern: "send email to a@gmail.com,b@gmail.com about Meeting tomorrow"
        m = re.search(r"send email to ([\w@.,]+) about (.+)", command, re.I)
        if m:
            to_emails = [email.strip() for email in m.group(1).split(",")]
            subject = "Automated Email from jarvis virtual assistant of reddypreetham20004@gmail.com"
            body = m.group(2)
        else:
            # fallback values
            to_emails = ["preethamreddyyelamancha@gmail.com"]
            subject = "Test Email"
            body = "This is a test email sent from Jarvis."

        # return send_email_cmd(to_emails, subject, body)
        return send_formatted_email_cmd(to_emails, subject, body)

    if "minimize" in c:
        m = re.search(r"minimize (.+)", c)
        return ScreenInteraction.minimize_window(m.group(1))

    if "close" in c:
        m = re.search(r"close (.+)", c)
        return ScreenInteraction.close_window(m.group(1))

    if "type" in c:
        m = re.search(r"type (.+) in (.+)", c)
        return ScreenInteraction.type_in_textbox(m.group(2), m.group(1))

    if "click" in c:
        m = re.search(r"click (.+) in (.+)", c)
        return ScreenInteraction.click_button(m.group(2), m.group(1))

     # Time/Date
    if "time" in c:
        return get_time()
    if "date" in c:
        return get_date()
    
    # fallback
    return "Sorry, I didn't understand that."
