import speech_recognition as sr
import threading

class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        try:
            self.microphone = sr.Microphone()
        except (OSError, AttributeError):
            # AttributeError is raised if PyAudio is missing
            print("No microphone detected or PyAudio missing.")
            self.microphone = None
            
    def listen(self, callback):
        """Listen for audio in a separate thread."""
        if not self.microphone:
            callback("Error: No microphone available.")
            return

        def _listen():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)
                    callback(text)
            except sr.WaitTimeoutError:
                callback("Error: Timeout")
            except sr.UnknownValueError:
                callback("Error: Could not understand audio")
            except Exception as e:
                callback(f"Error: {e}")

        threading.Thread(target=_listen, daemon=True).start()
