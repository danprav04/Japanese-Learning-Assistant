import speech_recognition as sr
from googletrans import Translator
from janome.tokenizer import Tokenizer
import jaconv
import keyboard
import tkinter as tk
from tkinter import font
import telebot

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def recognize_speech_from_mic(self):
        """Transcribe speech recorded from `microphone`."""

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening for your input...")
            audio = self.recognizer.listen(source)

        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            response["transcription"] = self.recognizer.recognize_google(audio, language="ja-JP")
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech"

        return response


class TextConverter:
    def __init__(self):
        self.tokenizer = Tokenizer()

    def convert_to_hiragana(self, text):
        tokens = self.tokenizer.tokenize(text)
        katakana_text = ''.join(token.reading for token in tokens if token.reading)
        hiragana_text = jaconv.kata2hira(katakana_text)
        return hiragana_text


class TranslatorService:
    def __init__(self):
        self.translator = Translator()

    def translate_text(self, text):
        translation = self.translator.translate(text, src='ja', dest='en').text
        return translation


class PopupWindow:
    def __init__(self, transcription, hiragana, translation, telegram_bot=None):
        self.root = tk.Tk()
        self.root.title("Speech Recognition Results")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        popup_width = 400
        popup_height = 200
        x_position = (screen_width - popup_width) // 2
        y_position = (screen_height - popup_height) // 2

        self.root.geometry(f"{popup_width}x{popup_height}+{x_position}+{y_position}")
        self.root.attributes('-topmost', True)

        self.bold_font = font.Font(weight='bold', size=18)

        self.label1 = tk.Label(self.root, text=f"You said: {transcription}", font=self.bold_font)
        self.label1.pack()

        self.label2 = tk.Label(self.root, text=f"In Hiragana: {hiragana}", font=self.bold_font)
        self.label2.pack()

        self.label3 = tk.Label(self.root, text=f"Translation: {translation}", font=self.bold_font)
        self.label3.pack()

        self.root.mainloop()

        # Send to Telegram
        if telegram_bot:
            self.send_to_telegram(telegram_bot, transcription, hiragana, translation)

    def send_to_telegram(self, bot, transcription, hiragana, translation):
        chat_id = '823900182'  # Replace with your Telegram chat ID
        message = f"You said: {transcription}\nIn Hiragana: {hiragana}\nTranslation: {translation}"
        bot.send_message(chat_id, message)


class SpeechRecognitionApp:
    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.text_converter = TextConverter()
        self.translator_service = TranslatorService()
        self.telegram_bot = telebot.TeleBot('7383089089:AAH81-9AOZRKFIBRkEkMNgYg31gvf4Cs83U')  # Replace with your Telegram bot token

    def run(self):
        print("Press F10 to start listening for Japanese input...")
        keyboard.wait('F10')
        print("Say something in Japanese!")

        response = self.speech_recognizer.recognize_speech_from_mic()

        if response["success"]:
            transcription = response["transcription"]
            hiragana = self.text_converter.convert_to_hiragana(transcription)
            translation = self.translator_service.translate_text(transcription)

            PopupWindow(transcription, hiragana, translation, self.telegram_bot)
        else:
            print("I didn't catch that. Error: {}".format(response["error"]))


if __name__ == "__main__":
    app = SpeechRecognitionApp()
    app.run()
