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
#             voice_output.say_and_wait(response)
#     else:
#         voice_output.say_and_wait("I didn't catch that. Please try again.")
    
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

import os
import sys
import json
import argparse
from time import sleep
from core import commands
from utils import voice_output, voice_input

def run_assistant_session(prebuffer_path=None):
    """
    Runs a single session of the AI assistant.
    Handles both live microphone input and pre-buffered audio from hotword_server.
    """
    print(" Assistant activated. Listening for command...")

    command = None

    # 1️⃣ If we received pre-buffered audio (after hotword trigger)
    if prebuffer_path and os.path.exists(prebuffer_path):
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
                command = voice_input.listen()
        except Exception as e:
            print(f"[ERROR] Failed to process prebuffer audio: {e}")
            command = voice_input.listen()

        # Remove temp file safely
        try:
            os.remove(prebuffer_path)
            print(f"[CLEANUP] Deleted temporary audio file: {prebuffer_path}")
        except Exception as e:
            print(f"[WARN] Could not delete temp file: {e}")

    # 2️⃣ If no prebuffer, fall back to real-time listening
    else:
        print("[INFO] No prebuffer found. Listening via microphone.")
        command = voice_input.listen()

    # 3️⃣ Handle the command
    if command:
        print(f"You said: {command}")
        response = commands.handle_command(command)
        if response:
            print(f"Jarvis: {response}")
            voice_output.say_and_wait(response)
        else:
            voice_output.say_and_wait("Sorry, I didn't understand that.")
    else:
        print("[WARN] No command detected.")
        voice_output.say_and_wait("I didn't catch that. Please try again.")

    print("Assistant session ending...")

# --- Entry Point ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jarvis Assistant Session")
    parser.add_argument("--prebuffer", type=str, help="Path to prebuffered audio file")
    args = parser.parse_args()

    run_assistant_session(prebuffer_path=args.prebuffer)
