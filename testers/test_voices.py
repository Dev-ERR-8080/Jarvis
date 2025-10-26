import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for idx, v in enumerate(voices):
    print(idx, v.name, v.id)

engine.setProperty('voice', voices[0].id)  # force default
engine.say("Testing voice output")
engine.runAndWait()
