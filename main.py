import speech_recognition as sr
import pyttsx3
import webbrowser
import musiclibrary
import datetime
import random
import wikipedia
import pyjokes
import yt_dlp
import os

from vectorstore import VectorStore
from retriever import Retriever
from embeddings import chunk_text, preprocess_document
from ingest import load_user_preferences as ingest_load_user_preferences
from commands import handle_rag_commands, format_response_with_context
import users  # PHASE 5: User Management




recogniser =  sr.Recognizer()
engine = pyttsx3.init()


def _initialize_rag_components():
    try:
        store = VectorStore(model_name="all-MiniLM-L6-v2")
        return store, Retriever(store)
    except Exception as exc:
        print(f"RAG initialization warning: {exc}")
        return None, None


vector_store, retriever = _initialize_rag_components()


def get_current_user():
    """Get current user ID from users module."""
    return users.get_current_user()


def initialize_user_knowledge(user_id="default"):
    if vector_store is None:
        return user_id

    path = os.path.join("user_data", user_id, "vectorstore.pkl")
    if os.path.exists(path):
        try:
            vector_store.load(path)
        except Exception as exc:
            print(f"Knowledge load warning for {user_id}: {exc}")
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    return user_id


def switch_user(user_id):
    """Switch to a different user (uses users module)."""
    if not user_id or not str(user_id).strip():
        return False
    
    user_id = str(user_id).strip()
    success = users.switch_user(user_id)
    if success:
        initialize_user_knowledge(user_id)
    return success


def persist_current_user_knowledge():
    if vector_store is None:
        return
    path = os.path.join("user_data", get_current_user(), "vectorstore.pkl")
    try:
        vector_store.save(path)
    except Exception as exc:
        print(f"Knowledge save warning: {exc}")


def set_voice(rate=160, voice_index=2):
    engine.setProperty('rate', rate)             # 100–200 (default: ~160)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[voice_index].id)

set_voice(180)
def speak(text):
    import traceback
    print(f"Assistant: {text}", flush=True)
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("speak error:", repr(e))
        traceback.print_exc()



#Greeting

def getGreeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning, Sudarshan Sir. How can i help you?"
    elif 12 <= hour < 17:
        return "Good afternoon, Sudarshan Sir. How can i help you?"
    elif 17 <= hour < 24:
        return "Good evening, Sudarshan Sir. How can i help you?"
    else:
        return "Working late, Sudarshan Sir? I'm here if you need me."


def listen_to_command():
    try:
        with sr.Microphone() as source:
            recogniser.adjust_for_ambient_noise(source, duration=0.3)
            audio = recogniser.listen(source, timeout=4, phrase_time_limit=6)
        return recogniser.recognize_google(audio)
    except Exception:
        return ""


def processCommand(c):
    user_id = get_current_user()
    command_lower = c.lower().strip()
    rag_context = []
    if retriever is not None:
        try:
            rag_context = retriever.retrieve(c, user_id=user_id, top_k=3)
        except Exception as exc:
            print(f"Retriever warning: {exc}")

    if retriever is not None and vector_store is not None:
        handled = handle_rag_commands(
            command_text=c,
            current_user=user_id,
            retriever=retriever,
            vector_store=vector_store,
            speak=speak,
            listen_to_command=listen_to_command,
            switch_user=switch_user,
        )
        if handled:
            persist_current_user_knowledge()
            return
    
 #Opening something   
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
        speak("sure,Sir")

    elif "open canva" in c.lower():
        webbrowser.open("https://www.canva.com/")
        speak("sure,Sir")
    
    elif "open linkedin" in c.lower():
        webbrowser.open("https://www.linkedin.com")
        speak("sure,Sir")

    elif "open my github profile" in c.lower():
        webbrowser.open("https://github.com/SudharshanDongre")
        speak("sure,Sir")

    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
        speak("sure,Sir")

    elif "joke" in  c:
        joke = pyjokes.get_joke()
        speak(joke)

#search on youtube
    elif "play" in c and "on youtube" in c.lower():
        search = c.lower().replace("play", "").replace("on youtube", "").strip()
        if search:
            speak(f"Sure, playing {search} on YouTube.")
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'default_search': 'ytsearch',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{search}", download=False)
                    if info and 'entries' in info and len(info['entries']) > 0:
                        video_url = info['entries'][0]['webpage_url']
                        webbrowser.open(video_url)
                    else:
                        speak("Sorry, I couldn't find any videos for that search.")
            except Exception as e:
                speak("Sorry, there was an error searching YouTube.")
                print(f"YouTube search error: {e}")
        else:
            speak("What should I play on YouTube, Sir?")

#search on google
    elif "search" in c:
        query = c.replace("search", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"Searching Google for {query}")


    elif "play music" in c or "play song" in c:
        speak("sure,which song you want to play from below?")
        print(musiclibrary.music.keys())


#you can build your own songs library
    elif c.lower().startswith("play" or "can you play"):
        song = c.lower().replace("play","",1).replace("can you play","",1).strip()
        if song in musiclibrary.music:
            link= musiclibrary.music[song]
            webbrowser.open(link)
            speak("sure playing it on youtube")
        else:
            speak(f"Sorry,I couldn't find {song} in your musiclibrary")


#Date & Time
    elif "time" in c:
         now = datetime.datetime.now().strftime("%I:%M %p")
         speak(f"The time is {now}")

    elif "date" in c:
        today = datetime.datetime.now().strftime("%A, %B %d")
        speak(f"Today is {today}")

#general questions
    elif "how are you" in  c or "kaise ho" in c or "how r u" in c:
        response=[
            "All systems are green and operational, How are you,sir?",
            "I'm running at full capacity. Systems online, How can I help you.",
            "At your service, as always. how are you,sir?.",
            "Feeling pretty electric today, how are you,Sir.",
            "I'm Alright sir, System is performance is 100 % , how can i help you?"
        ]
        set_voice(rate=160)
        speak(random.choice(response))
    elif "fine" in c or "theek hu" in c:
        speak("Great,How can i help you?")

    elif "who are you" in c or "hu r u" in c:
        speak("I am Ultron, version 1.0 — created by Mr. Dongre.")


    elif "who invented you" in c:
        speak("I was created by Mr.Dongre — the one and only.")

    elif "hello" in c.lower():
        speak(getGreeting())
   
    elif "what can you do" in c or "your abilities" in c or "tum kya kar sakte ho" in c:
        base_response = "I can open different sites, play music, answer questions, make jokes, and can also convert your imagination into reality. Just say the word."
        context_prefix = format_response_with_context(rag_context)
        enhanced_response = f"{context_prefix}. {base_response}" if context_prefix else base_response
        set_voice(rate=160)
        speak(enhanced_response)

    elif "introduce yourself" in c:
        speak("I am Ultron — the bridge between your command and execution. Think it. Say it. I’ll make it happen.")

    elif "what are you doing" in c or "what r u doing"in c or "kya kar rahe ho" in  c:
        speak("Doing exactly what you designed me to do: be excellent.")

    elif "ultron" in c.lower():
        speak("Yes Sir!")

    elif "nice to meet you" in c or "good to know you" in c:
        speak("Nice to meet you as well. I'm here to assist whenever you need me.")




#For closeing 
    elif "exit" in c or "stop listening" in c or "good bye" in  c or "goodbye" in c or "bye" in c:
        persist_current_user_knowledge()
        speak("Shutting down. Goodbye, Sir.")
        
        exit()

    # Personal questions should try memory first before any web fallback.
    elif (
        any(word in command_lower for word in ["what", "who", "how"])
        and any(phrase in command_lower for phrase in [" my ", "about me", "my name", "i prefer", "i like", "me "])
    ):
        if rag_context:
            set_voice(rate=160)
            speak(format_response_with_context(rag_context))
        else:
            prefs = load_user_preferences(user_id)
            user_name = str(prefs.get("username", "")).strip()
            if "name" in command_lower and user_name:
                speak(f"Your name is {user_name}.")
            else:
                speak("I do not have that in memory yet. You can teach me by saying add to my knowledge followed by your note.")

#serach on wikipedia
    elif command_lower.startswith(("what is", "who is", "tell me about", "how to", "how does", "what are", "who are")):
        try:
            question = (
                command_lower
                .replace("what is", "")
                .replace("who is", "")
                .replace("tell me about", "")
                .replace("how to", "")
                .replace("how does", "")
                .replace("what are", "")
                .replace("who are", "")
                .strip()
            )
            result=wikipedia.summary(question,sentences=1)
            set_voice(rate=160)
            speak(f"{result}")
        
        
        except wikipedia.exceptions.PageError:
            speak("I couldn’t find anything on that topic, Sir.")

        except wikipedia.exceptions.DisambiguationError as e:
            speak(f"There are multiple results. Try being more specific.")

        except Exception as e:
            print(e)

    else:
        # Fallback for unrecognized commands
        speak("Sorry Sir, I didn't understand that command. Could you please repeat?")

        
    
        


if __name__ == "__main__":
    # speak("Initializing Ultron..")
    initialize_user_knowledge(get_current_user())
    try:
        load_user_preferences(get_current_user())
    except Exception as exc:
        print(f"Preferences warning: {exc}")
    speak("Ultron systems Activated. Awaiting for your command Sir.")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recogniser.adjust_for_ambient_noise(source, duration=0.5)
                # audio = recogniser.listen(source, timeout=5, phrase_time_limit=3)
                recogniser.pause_threshold = 0.5  # Reacts faster to short pauses
                audio = recogniser.listen(source, timeout=2, phrase_time_limit=3)
                # print("Recognising...")
                command = recogniser.recognize_google(audio)
                print("Heard:", command)
                processCommand(command)

        except sr.WaitTimeoutError:
            print('WaitTimeoutError: microphone timed out, continuing')
            continue
        except sr.UnknownValueError:
            print('UnknownValueError: could not understand audio, continuing')
            continue
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
        except Exception as e:
            print("Error:", e)

    # while True:
        #listen for the wake word "Ultron"
        #obtain audio from microphone
    #older code! wake only when ultron name is called!
    '''  r=sr.Recognizer()



        print("Recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recogniser.adjust_for_ambient_noise(source, duration=0.5)
                audio=r.listen(source,timeout=2,phrase_time_limit=1)
                command=r.recognize_google(audio)
                if (command.lower()=="ultron"):
                    speak("Yes sir")
                    #listen for command
                    with sr.Microphone() as source:
                        print("Ultron Activated...")
                        # recogniser.adjust_for_ambient_noise(source,duration=0.5)
                        audio=r.listen(source)
                        command=r.recognize_google(audio)

                        processCommand(command)


        except Exception as e:
            print("Error; {0}".format(e))
'''
