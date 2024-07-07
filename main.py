import speech_recognition as sr
from googletrans import Translator
from janome.tokenizer import Tokenizer
import jaconv
import keyboard
import telebot
import winsound


class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def recognize_speech_from_mic(self):
        """Transcribe speech recorded from `microphone`."""

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            winsound.Beep(1000, 300)
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


class TelegramSender:
    def __init__(self, bot_token, chat_id):
        self.bot = telebot.TeleBot(bot_token)
        self.chat_id = chat_id

    def send_message(self, message):
        self.bot.send_message(self.chat_id, message, parse_mode='Markdown')


class SpeechRecognitionApp:
    def __init__(self, bot_token, chat_id):
        self.speech_recognizer = SpeechRecognizer()
        self.text_converter = TextConverter()
        self.translator_service = TranslatorService()
        self.telegram_sender = TelegramSender(bot_token, chat_id)

    def run(self):
        print("Press F10 to start listening for Japanese input...")
        keyboard.wait('F10')
        print("Say something in Japanese!")

        response = self.speech_recognizer.recognize_speech_from_mic()

        if response["success"]:
            transcription = response["transcription"]
            hiragana = self.text_converter.convert_to_hiragana(transcription)
            translation = self.translator_service.translate_text(transcription)

            self.send_to_telegram(transcription, hiragana, translation)
        else:
            print("I didn't catch that. Error: {}".format(response["error"]))

    def send_to_telegram(self, transcription, hiragana, translation):
        link = f"[Detailed Parsing](https://ichi.moe/cl/qr/?q={transcription}&r=htr)"
        message = f"You said: {transcription}\nIn Hiragana: {hiragana}\nTranslation: {translation}\n{link}"
        self.telegram_sender.send_message(message)


if __name__ == "__main__":
    bot_token = '7383089089:AAH81-9AOZRKFIBRkEkMNgYg31gvf4Cs83U'  # Replace with your Telegram bot token
    chat_id = '823900182'  # Replace with your Telegram chat ID
    app = SpeechRecognitionApp(bot_token, chat_id)

    while True:
        app.run()
