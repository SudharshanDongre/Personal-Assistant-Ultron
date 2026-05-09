# Voice Assistant 🎤

A Python-based voice-activated personal assistant that listens to commands and responds using text-to-speech. The assistant can open websites, play music, search the web, fetch information, and tell jokes—all through voice interaction.

## Features 🚀

- **Voice Recognition**: Listens to voice commands using the SpeechRecognition library
- **Text-to-Speech**: Responds with natural-sounding speech using pyttsx3
- **Web Browsing**: Open websites like Google, YouTube, LinkedIn, Canva, and more
- **Music Playback**: Play songs from a customizable music library directly on YouTube
- **Web Search**: Search Google or YouTube for any query
- **Information Lookup**: Retrieve information from Wikipedia
- **Entertainment**: Tell jokes using pyjokes
- **Time-Based Greetings**: Personalized greetings based on time of day
- **Customizable Voice**: Adjustable voice speed and voice index

## Supported Commands 🎯

### Website Commands
- "open google" - Opens Google
- "open youtube" - Opens YouTube
- "open linkedin" - Opens LinkedIn
- "open canva" - Opens Canva
- "open my github profile" - Opens GitHub profile

### Music & Entertainment
- "play music" or "play song" - View available songs and play them
- "play [song name]" - Play a specific song from the music library
- "joke" - Tell a random joke

### Search Commands
- "search [query]" - Search on Google
- "play [query] on youtube" - Search and play videos on YouTube

### Information
- Access Wikipedia information (via configured commands)

## Installation 📦

1. **Clone or download this project**
   ```bash
   cd "c:\Python\MEGA PROJECT 1"
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies
- **SpeechRecognition** - Voice input processing
- **pyttsx3** - Text-to-speech output
- **wikipedia** - Wikipedia information retrieval
- **pyjokes** - Joke generation
- **gTTS** - Google Text-to-Speech
- **deep-translator** - Translation support
- **pygame** - Audio playback
- **google-generative-ai** - (Optional) Google Gemini AI integration

## Usage 🎮

1. **Run the assistant**
   ```bash
   python main.py
   ```

2. **Start giving voice commands** once the assistant greets you

3. **Example commands**:
   - "open google"
   - "play barrish on youtube"
   - "search python tutorials"
   - "tell me a joke"
   - "play tum hi ho"

## Project Structure 📁

```
├── main.py              # Main entry point with command processing
├── commands.py          # Command handling and definitions
├── musiclibrary.py      # Music library with YouTube links
├── voices.py            # Voice configuration and settings
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Music Library 🎵

The music library is stored in `musiclibrary.py` and contains Hindi songs with direct YouTube links. You can easily add more songs by editing the dictionary:

```python
music={
    "song name" : "https://youtube.com/watch?v=...",
    # Add more songs here
}
```

## Customization ⚙️

### Change Voice Properties
Edit the `set_voice()` function in `main.py`:
```python
def set_voice(rate=160, voice_index=2):
    engine.setProperty('rate', rate)      # Speed: 100-200
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[voice_index].id)
```

### Add New Commands
Modify the `processCommand()` function in `main.py` to add custom commands

### Extend Music Library
Add songs to the `music` dictionary in `musiclibrary.py`

## Future Enhancements 🔮

- [ ] Integrate Google Gemini AI for intelligent responses (currently commented out)
- [ ] Add weather information
- [ ] Email sending capability
- [ ] Calendar integration
- [ ] File management commands
- [ ] System control commands

## Requirements Notes ⚠️

- **Microphone**: Required for voice input
- **Internet Connection**: Needed for web browsing, music playback, and information retrieval
- **Google Gemini Integration**: Requires manual installation of google-generative-ai package and API key setup

## Troubleshooting 🔧

- **Microphone not detected**: Check system audio settings and microphone permissions
- **Speech not recognized**: Speak clearly and adjust background noise
- **Voice commands not working**: Ensure microphone is properly configured
- **Import errors**: Reinstall requirements with `pip install -r requirements.txt`

## Author

Created for personal assistance and automation

## License

Feel free to use and modify as needed

---

**Happy commanding!** 🎙️
