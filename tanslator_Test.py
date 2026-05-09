from gtts import gTTS
from deep_translator import GoogleTranslator
import pygame
import time


# Translate to Marathi
translator = GoogleTranslator(source='auto', target='mr')
text = translator.translate("how are you")

# Convert to speech
tts = gTTS(text=text, lang='mr')
tts.save("output.mp3")

# Initialize the pygame mixer
pygame.mixer.init()

# Load the audio file
pygame.mixer.music.load("output.mp3")

# Play the audio
pygame.mixer.music.play()

# Wait for the music to finish playing
while pygame.mixer.music.get_busy():
    time.sleep(1)

