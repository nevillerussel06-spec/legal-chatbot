import pyttsx3
import speech_recognition as sr
import threading
import queue
import time
from groq import Groq
from dotenv import load_dotenv
import os
# =====================================================
# GROQ API SETUP
# =====================================================
# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")  # Replace with your actual Groq API key
client = Groq(api_key=API_KEY)

# =====================================================
# TEXT TO SPEECH SETUP
# =====================================================

engine = pyttsx3.init()

voices = engine.getProperty('voices')

# Male voice
engine.setProperty('voice', voices[0].id)

# Speech speed
engine.setProperty('rate', 165)

# Volume
engine.setProperty('volume', 2.0)

# Prevent TTS overlap
speech_queue = queue.Queue()

# =====================================================
# SPEAK FUNCTION
# =====================================================

def tts_worker():
    while True:
        text = speech_queue.get()
        if text is None:
            break
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("TTS Error:", e)
        speech_queue.task_done()

# Start TTS thread
threading.Thread(target=tts_worker, daemon=True).start()

def speak(text):
    print("\nlawbot:", text)
    speech_queue.put(text)

# =====================================================
# SPEECH TO TEXT SETUP
# =====================================================

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.pause_threshold = 1

# =====================================================
# LISTEN FUNCTION
# =====================================================

def listen():
    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=15
            )
            print("Recognizing...")
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError as e:
            print("Speech service error:", e)
            return None
        except Exception as e:
            print("Speech Error:", e)
            return None

# =====================================================
# AI LEGAL ASSISTANT
# =====================================================

conversation_history = []

SYSTEM_PROMPT = """
You are lawbot, an AI Legal Assistant for Indian law.

Your behavior:
- Explain Indian laws clearly
- Analyze the user's legal issue first
- Mention possible legal rights and risks
- Suggest practical next steps
- Use simple language
- Stay professional and calm
- Never encourage illegal actions
- Never claim to be a licensed advocate
- Recommend consulting a real lawyer for serious legal matters

Response Format:
1. Legal Analysis
2. Possible Legal Position
3. Recommended Action

Keep responses concise and understandable.
"""

def ask_lawbot(question):
    try:
        conversation_history.append({
            "role": "user",
            "content": question
        })

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        # Add conversation memory
        messages.extend(conversation_history[-10:])

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=1024
        )

        answer = completion.choices[0].message.content

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:
        return f"API Error: {e}"

# =====================================================
# MAIN PROGRAM
# =====================================================

def main():
    speak("Hello. I am lawbot, your AI Legal Assistant.")

    while True:
        print("\n=========== MENU ===========")
        print("1. Type Question")
        print("2. Speak Question")
        print("3. Continuous Voice Mode")
        print("4. Exit")

        choice = input("\nEnter choice: ").strip()

        # TYPE QUESTION
        if choice == "1":
            question = input("\nAsk your legal question:\n> ")
            if question.lower() in ["exit", "quit", "stop"]:
                break
            response = ask_lawbot(question)
            speak(response)

        # SPEAK QUESTION
        elif choice == "2":
            question = listen()
            if question:
                if question.lower() in ["exit", "quit", "stop"]:
                    break
                response = ask_lawbot(question)
                speak(response)
            else:
                speak("Sorry, I could not understand.")

        # CONTINUOUS VOICE MODE
        elif choice == "3":
            speak("Continuous voice mode activated.")
            while True:
                question = listen()
                if not question:
                    continue
                if question.lower() in ["exit", "quit", "stop"]:
                    speak("Exiting voice mode.")
                    break
                response = ask_lawbot(question)
                speak(response)
                time.sleep(1)

        # EXIT
        elif choice == "4":
            speak("Goodbye.")
            break

        else:
            speak("Invalid choice.")

# =====================================================
# START PROGRAM
# =====================================================

if __name__ == "__main__":
    main()

def chatbot_response(text):
    return ask_lawbot(text)
