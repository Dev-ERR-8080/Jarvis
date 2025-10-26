import speech_recognition as sr

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I did not get that.")
        return ""
    except sr.RequestError:
        print("Speech service error")
        return ""
def transcribe_file(path: str) -> str | None:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return None


# utils/voice_input.py
# import speech_recognition as sr
# import numpy as np

# recognizer = sr.Recognizer()

# def listen(prebuffer=None):
#     """
#     Capture user speech either from pre-buffered audio or live mic.
#     prebuffer: list/queue of PCM frames (int16)
#     """
#     try:
#         if prebuffer:
#             print("[DEBUG] Using pre-buffered audio")
#             audio = sr.AudioData(prebuffer, sample_rate=16000, sample_width=2)
#             return recognizer.recognize_google(audio).lower()

#         # fallback to live mic
#         with sr.Microphone() as source:
#             print("Listening on microphone…")
#             audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
#             return recognizer.recognize_google(audio).lower()

#     except sr.UnknownValueError:
#         return None
#     except sr.RequestError as e:
#         print("STT error:", e)
#         return None
# def transcribe_file(path: str) -> str | None:
#     import speech_recognition as sr
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(path) as source:
#         audio = recognizer.record(source)
#     try:
#         return recognizer.recognize_google(audio)
#     except sr.UnknownValueError:
#         return None
