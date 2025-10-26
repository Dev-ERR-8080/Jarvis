import queue
import threading
import win32com.client
import pythoncom

class SapVoiceWorker:
    def __init__(self):
        self.queue = queue.Queue()
        self.running = False
        self.thread = None

    def _worker(self):
        # Initialize COM in this thread
        pythoncom.CoInitialize()

        speaker = win32com.client.Dispatch("SAPI.SpVoice")

        while self.running:
            try:
                text = self.queue.get(timeout=0.5)
                if text is None:
                    break
                speaker.Speak(text)
            except queue.Empty:
                continue

        pythoncom.CoUninitialize()  # Clean up when done

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
        print(f"Jarvis says: {text}")
        self.queue.put(text)


if __name__ == "__main__":
    tts = SapVoiceWorker()
    tts.start()

    print("Queuing messages...")
    tts.say("Hello, I am Jarvis.")
    tts.say("This is the second test message.")
    tts.say("Now, the third message should also be spoken.")

    import time
    time.sleep(10)

    tts.stop()
