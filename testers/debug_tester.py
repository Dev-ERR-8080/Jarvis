# test_speak_batch.py
from utils.voice_output import speak
speak("first message")
speak("second message")
speak("third message")
# allow worker to flush
import time; time.sleep(6)
print("done")
