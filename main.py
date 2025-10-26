# from core import commands, scheduler
# from utils import voice_output, notifier


# def main():
#     voice_output.speak("Jarvis is online.")
#     # scheduler.load_and_restore() already runs on import in core.scheduler
#     while True:
#         try:
#             command = input("You: ").strip()
#             if command.lower() == "voice":
#                 from utils import voice_input
#                 command = voice_input.listen()
#         except (EOFError, KeyboardInterrupt):
#             voice_output.speak("Shutting down. Goodbye!")
#             break

#         if not command:
#             continue

#         response = commands.handle_command(command)
#         # send response to TTS
#         # print("response from jarvis: " + response)
#         voice_output.speak(response)

#         if response == "Goodbye!":
#             break

# if __name__ == "__main__":
#     main()
# main.py
# main.py
import time
from core import commands
from utils import voice_output, voice_input
from utils.voice_output import SapVoiceWorker

voice_output = SapVoiceWorker()
voice_output.start()

def main():
    
    while True:
        try:
            print("Listening for a command...")
            
            # Choose input mode
            command = input("You: ").strip()

            if command == "voice":
                print("please type your command...")
                command = voice_input.listen().strip().lower()
            if not command:
                continue

            # Process command
            response = commands.handle_command(command)

            if response:
                # print("Response from Jarvis:", response)  # Always print
                voice_output.say(response)             # Always say

                # Exit condition
                if "goodbye" in response.lower():
                    break

            time.sleep(0.5)

        except (EOFError, KeyboardInterrupt):
            print("KeyboardInterrupt detected. Shutting down gracefully...")
            voice_output.say("Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            voice_output.say("I encountered an error. Please try again.")
            continue

if __name__ == "__main__":
    main()
