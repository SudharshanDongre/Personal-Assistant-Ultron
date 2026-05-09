import speech_recognition as sr
import pyttsx3
import webbrowser
import musiclibrary
import datetime
import random
import wikipedia
import pyjokes




recogniser =  sr.Recognizer()
engine = pyttsx3.init()
def set_voice(rate=160, voice_index=2):
    engine.setProperty('rate', rate)             # 100–200 (default: ~160)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[voice_index].id)

set_voice(180)
def speak(text):
    engine.say(text)
    engine.runAndWait()



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


def processCommand(c):
    
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
            query = search.replace(" ", "+")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
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
       set_voice(rate=160)
       speak("I can open different sites, play music, answer questions, make jokes, and can also convert your imagination into reality. Just say the word.")

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
        speak("Shutting down. Goodbye, Sir.")
        
        exit()

#serach on wikipedia
    elif "what is" in c or "who is" in c or "tell me about" in c or "who" in c or "what" in c or "how" in c:
        try:
            question= c.lower().replace("what is","").replace("who is","").replace("tell me about","").replace("who","").replace("what","").replace("how","").strip()
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
            speak("I didn't hear anything. Please try again.")  # Timeout feedback
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you please repeat?")  # Unrecognized speech feedback
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
