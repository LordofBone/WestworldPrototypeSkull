import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
print(voices)
engine.setProperty('voice', voices[2].id)
engine.say("Hi, Welcome to Circuit Digest Tutorial")
engine.runAndWait()
