import debug_voice_output
import time

print("Queuing messages...")
debug_voice_output.speak("Hello, I am Jarvis.")
debug_voice_output.speak("This is the second test message.")
debug_voice_output.speak("Now, the third message should also be spoken.")

time.sleep(10)  # wait while messages play
