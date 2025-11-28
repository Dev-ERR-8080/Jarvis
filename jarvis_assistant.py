# import os
# import sys
# from PyQt6.QtWidgets import QApplication
# from ui.simple_test_ui import run_simple_ui
# from time import sleep
# from core import commands
# from utils import voice_output, voice_input


# def run_assistant_session(prebuffer_path):
#     """Runs a single session of the AI assistant."""

#     print("Assistant activated. Jarvis is listening...")
#     # voice_output.say("Hello sir, how can I help you?")
    
#     # sleep(1.5)
#     if prebuffer_path and os.path.exists(prebuffer_path):
#         print("[DEBUG] Using pre-buffered audio")
#         command = voice_input.transcribe_file(prebuffer_path)
#         if command:
#             command = command.lower().strip()
#             # strip the hot-word if it appears at the start
#             if command.startswith("jarvis"):
#                 # remove "jarvis" and following comma/space
#                 command = command.replace("jarvis", "", 1).lstrip(" ,.")
#             print(f"Detected command: {command}")
#         else:
#             command = voice_input.listen()   # normal live listening

#     if command:
#         print(f"You said: {command}")
#         response = commands.handle_command(command)
#         if response:
#             # window.add_message(f"Jarvis: {response}")
#             voice_output.say(response)
#     else:
#         voice_output.say("I didn't catch that. Please try again.")
    
#     print("Assistant session ending...")
    
#     #  sys.exit(app.exec())


# if __name__ == "__main__":
#     prebuffer_path = None
#     # parse CLI args
#     if "--prebuffer" in sys.argv:
#         idx = sys.argv.index("--prebuffer") + 1
#         if idx < len(sys.argv):
#             prebuffer_path = sys.argv[idx]
#             if not os.path.exists(prebuffer_path):
#                 print(f"[WARN] Prebuffer file not found: {prebuffer_path}")
#                 prebuffer_path = None

#     run_assistant_session(prebuffer_path=prebuffer_path)

# import os
# import sys
# import json
# import argparse
# from time import sleep
# from core import commands
# from utils import voice_output, voice_input

# def run_assistant_session(prebuffer_path=None):
#     """
#     Runs a single session of the AI assistant.
#     Handles both live microphone input and pre-buffered audio from hotword_server.
#     """
#     print(" Assistant activated. Listening for command...")

#     command = None
    
#     # 1️⃣ If we received pre-buffered audio (after hotword trigger)
#     if prebuffer_path and os.path.exists(prebuffer_path):
#         print(f"[DEBUG] Using pre-buffered audio file: {prebuffer_path}")
#         try:
#             command = voice_input.transcribe_file(prebuffer_path)
#             if command:
#                 command = command.lower().strip()
#                 # Remove wake word ("jarvis") if present
#                 if command.startswith("jarvis"):
#                     command = command.replace("jarvis", "", 1).lstrip(" ,.")
#                 print(f"[DEBUG] Transcribed command: '{command}'")
#             else:
#                 print("[WARN] Transcription failed or empty. Falling back to live listening.")
#                 command = voice_input.listen()
#         except Exception as e:
#             print(f"[ERROR] Failed to process prebuffer audio: {e}")
#             command = voice_input.listen()

#         # Remove temp file safely
#         try:
#             os.remove(prebuffer_path)
#             print(f"[CLEANUP] Deleted temporary audio file: {prebuffer_path}")
#         except Exception as e:
#             print(f"[WARN] Could not delete temp file: {e}")

#     # 2️⃣ If no prebuffer, fall back to real-time listening
#     else:
#         print("[INFO] No prebuffer found. Listening via microphone.")
#         command = voice_input.listen()

#     # 3️⃣ Handle the command
#     if command:
#         print(f"You said: {command}")
#         response = commands.handle_command(command)
#         if response:
#             print(f"Jarvis: {response}")
#             voice_output.say(response)
#         else:
#             voice_output.say("Sorry, I didn't understand that.")
#     else:
#         print("[WARN] No command detected.")
#         voice_output.say("I didn't catch that. Please try again.")

#     print("Assistant session ending...")

# # --- Entry Point ---
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Jarvis Assistant Session")
#     parser.add_argument("--prebuffer", type=str, help="Path to prebuffered audio file")
#     args = parser.parse_args()

#     run_assistant_session(prebuffer_path=args.prebuffer)

import os
import sys
import argparse
import time # <-- Imported time for timing
from core import commands
from utils import voice_output, voice_input

def run_assistant_session(prebuffer_path=None):
    """
    Runs a single session of the AI assistant.
    Handles both live microphone input and pre-buffered audio from hotword_server.
    """
    
    # --- PHASE 1: STARTUP/SETUP ---
    startup_start_time = time.time()
    
    print(" Assistant activated. Listening for command...")
    command = None
    
    # -----------------------------------
    startup_end_time = time.time()
    print(f"[TIMING] Phase 1 (Startup/Imports): {startup_end_time - startup_start_time:.3f}s")
    # -----------------------------------
    
    # 1️⃣ If we received pre-buffered audio (after hotword trigger)
    if prebuffer_path and os.path.exists(prebuffer_path):
        
        # --- PHASE 2A: TRANSCRIPTION (Pre-buffered) ---
        transcription_start_time = time.time()
        
        print(f"[DEBUG] Using pre-buffered audio file: {prebuffer_path}")
        try:
            command = voice_input.transcribe_file(prebuffer_path)
            
            if command:
                command = command.lower().strip()
                # Remove wake word ("jarvis") if present
                if command.startswith("jarvis"):
                    command = command.replace("jarvis", "", 1).lstrip(" ,.")
                print(f"[DEBUG] Transcribed command: '{command}'")
            else:
                print("[WARN] Transcription failed or empty. Falling back to live listening.")
                command = voice_input.listen() # This will be slow if the live listen involves more setup
        except Exception as e:
            print(f"[ERROR] Failed to process prebuffer audio: {e}")
            command = voice_input.listen()
        
        # -----------------------------------
        transcription_end_time = time.time()
        print(f"[TIMING] Phase 2A (Transcription): {transcription_end_time - transcription_start_time:.3f}s")
        # -----------------------------------

        # Remove temp file safely
        try:
            os.remove(prebuffer_path)
            print(f"[CLEANUP] Deleted temporary audio file: {prebuffer_path}")
        except Exception as e:
            print(f"[WARN] Could not delete temp file: {e}")

    # 2️⃣ If no prebuffer, fall back to real-time listening
    else:
        # --- PHASE 2B: LIVE LISTENING ---
        live_listen_start_time = time.time()
        
        print("[INFO] No prebuffer found. Listening via microphone.")
        command = voice_input.listen()
        
        # -----------------------------------
        live_listen_end_time = time.time()
        print(f"[TIMING] Phase 2B (Live Listening): {live_listen_end_time - live_listen_start_time:.3f}s")
        # -----------------------------------


    # 3️⃣ Handle the command
    if command:
        print(f"You said: {command}")
        
        # --- PHASE 3: COMMAND EXECUTION (NLP/Action) ---
        command_exec_start_time = time.time()
        
        response = commands.handle_command(command)
        
        # -----------------------------------
        command_exec_end_time = time.time()
        print(f"[TIMING] Phase 3 (Command Execution): {command_exec_end_time - command_exec_start_time:.3f}s")
        # -----------------------------------
        
        # --- PHASE 4: VOICE OUTPUT ---
        voice_output_start_time = time.time()
        
        if response:
            print(f"Jarvis: {response}")
            voice_output.say(response)
        else:
            voice_output.say("Sorry, I didn't understand that.")
        
        # -----------------------------------
        voice_output_end_time = time.time()
        print(f"[TIMING] Phase 4 (Voice Output): {voice_output_end_time - voice_output_start_time:.3f}s")
        # -----------------------------------
    else:
        print("[WARN] No command detected.")
        voice_output.say("I didn't catch that. Please try again.")

    print("Assistant session ending...")

# --- Entry Point ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis Assistant Session")
    parser.add_argument("--prebuffer", type=str, help="Path to prebuffered audio file")
    args = parser.parse_args()

    # --- PHASE 0: TOTAL EXECUTION TIME ---
    total_start_time = time.time()
    
    run_assistant_session(prebuffer_path=args.prebuffer)

    total_end_time = time.time()
    print(f"\n[TIMING]  TOTAL ASSISTANT LATENCY: {total_end_time - total_start_time:.3f}s")