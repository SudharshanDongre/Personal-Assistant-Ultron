import pyttsx3

engine = pyttsx3.init()

# Get list of available voices
voices = engine.getProperty('voices')

# Print all available voices
for index, voice in enumerate(voices):
    print(f"Voice {index}: {voice.name} - {voice.id}")

# Set a specific voice by index
engine.setProperty('voice', voices[2].id)  # Change index: 0, 1, etc.

engine.say("Hello, this is your assistant.")
engine.runAndWait()
