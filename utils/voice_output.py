# import threading, time, atexit
# from typing import Optional
# import subprocess
# from utils.logger import logger

# try:
#     import pyttsx3
#     _has_pyttsx3 = True
# except Exception as e:
#     _has_pyttsx3 = False
#     logger = logger if 'logger' in globals() else None
#     if logger: logger.warning("pyttsx3 import failed: %s", e)

# _engine = None
# _engine_lock = threading.Lock()
# _queue = []
# _queue_lock = threading.Lock()
# _flush_event = threading.Event()
# _worker_thread: Optional[threading.Thread] = None
# _running = True

# def _init_engine():
#     global _engine
#     if not _has_pyttsx3:
#         return None
#     try:
#         with _engine_lock:
#             if _engine is None:
#                 _engine = pyttsx3.init()
#                 _engine.setProperty("rate", 150)
#                 logger.debug("pyttsx3 engine initialized")
#     except Exception as e:
#         logger.exception("Failed to init pyttsx3 engine: %s", e)
#         _engine = None
#     return _engine

# def _powershell_speak(text):
#     # safe single-quoted string
#     safe = text.replace("'", "''")
#     cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $s=(New-Object System.Speech.Synthesis.SpeechSynthesizer); $s.Speak(\'{safe}\')"'
#     try:
#         subprocess.run(cmd, shell=True, check=True)
#         logger.debug("PowerShell TTS succeeded")
#         return True
#     except Exception as e:
#         logger.exception("PowerShell TTS failed: %s", e)
#         return False

# def _worker():
#     # worker waits until _flush_event set; then flushes current queued texts in one runAndWait()
#     logger.debug("TTS worker started")
#     _init_engine()
#     while _running:
#         flush = _flush_event.wait(timeout=1.0)
#         if not flush:
#             continue
#         # Copy and clear the queue
#         with _queue_lock:
#             texts = list(_queue)
#             _queue.clear()
#         _flush_event.clear()
#         if not texts:
#             continue
#         joined = " . ".join(texts)  # join to speak sequentially w/ slight gap
#         try:
#             if _engine:
#                 with _engine_lock:
#                     _engine.say(joined)
#                     _engine.runAndWait()
#                     logger.debug("pyttsx3 spoke: %s", joined)
#             else:
#                 # fallback to powershell
#                 _powershell_speak(joined)
#         except Exception as e:
#             logger.exception("pyttsx3 run failed, falling back to powershell: %s", e)
#             _powershell_speak(joined)

# def start_worker():
#     global _worker_thread
#     if _worker_thread and _worker_thread.is_alive():
#         return
#     _worker_thread = threading.Thread(target=_worker, daemon=True)
#     _worker_thread.start()

# def stop_worker():
#     global _running
#     _running = False
#     _flush_event.set()
#     try:
#         if _engine:
#             with _engine_lock:
#                 _engine.stop()
#     except Exception:
#         pass

# # public API
# def speak(text: str):
#     if not text:
#         return
#     with _queue_lock:
#         _queue.append(str(text))
#     # signal worker to flush soon (you can tune to batch multiple small speeches)
#     _flush_event.set()

# # initialize
# start_worker()
# atexit.register(stop_worker)

#worked with the testers/debug_voice_output.py but not on main.py
import queue
import threading
import win32com.client
import pythoncom
import atexit
import time

class SapVoiceWorker:
    def __init__(self):
        self.queue = queue.Queue()
        self.running = False
        self.thread = None
        self.speaker = None

    def _worker(self):
        pythoncom.CoInitialize()
        try:
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
            while self.running:
                try:
                    text = self.queue.get(timeout=0.5)
                    if text is None:
                        break
                    self.speaker.Speak(text)
                except queue.Empty:
                    continue
        finally:
            pythoncom.CoUninitialize()

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._worker, daemon=True)
            self.thread.start()
            print("Speech thread started (SAPI).")

    def stop(self):
        if self.running:
            self.running = False
            self.queue.put(None)
            self.thread.join()
            print("Speech thread stopped.")
            
    def say(self, text: str):
        """Non-blocking: adds text to the queue to be spoken later."""
        print(f"Jarvis says: {text}")
        self.queue.put(text)

# --- CORRECTED BLOCKING METHOD ---
    def say_and_wait(self, text: str):
        """Blocking: speaks the text immediately and waits for it to finish."""
        print("jarvis (blocking):", text)
        try:
            # We don't use the queue here to avoid race conditions
            # Instead, we create a temporary speaker object
            temp_speaker = win32com.client.Dispatch("SAPI.SpVoice")
            temp_speaker.Speak(text)
            # No need for runAndWait or stop here, it's a synchronous call.
        except Exception as e:
            print(f"Error in blocking speech: {e}")

# Instantiate the worker and set up a graceful shutdown
tts_worker = SapVoiceWorker()
atexit.register(tts_worker.stop)
tts_worker.start()

# Expose module-level functions for the rest of your project to use
def say(text: str):
    tts_worker.say(text)

def say_and_wait(text: str):
    tts_worker.say_and_wait(text)