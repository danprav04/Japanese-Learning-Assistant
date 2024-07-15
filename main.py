import io
import speech_recognition as sr
from googletrans import Translator
from janome.tokenizer import Tokenizer
import jaconv
import telebot
import requests
import soundfile as sf


class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize_speech_from_audio(self, audio_data):
        """Transcribe speech from audio data."""
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            audio_file = sr.AudioFile(audio_data)
            with audio_file as source:
                audio = self.recognizer.record(source)
                response["transcription"] = self.recognizer.recognize_google(audio, language="ja-JP")
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech"
        except Exception as e:
            response["success"] = False
            response["error"] = str(e)

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


class TelegramHandler:
    def __init__(self, bot_token):
        self.bot = telebot.TeleBot(bot_token)

    def send_message(self, chat_id, message, reply_to_message_id=None):
        self.bot.send_message(chat_id, message, parse_mode='Markdown', reply_to_message_id=reply_to_message_id)

    def download_audio(self, file_id):
        file_info = self.bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{self.bot.token}/{file_info.file_path}"
        response = requests.get(file_url)
        return io.BytesIO(response.content)

    def convert_audio_to_wav(self, ogg_data):
        data, samplerate = sf.read(ogg_data)
        wav_io = io.BytesIO()
        sf.write(wav_io, data, samplerate, format='WAV')
        wav_io.seek(0)  # Seek to the start of the BytesIO object
        return wav_io


class SpeechRecognitionApp:
    def __init__(self, bot_token):
        self.speech_recognizer = SpeechRecognizer()
        self.text_converter = TextConverter()
        self.translator_service = TranslatorService()
        self.telegram_handler = TelegramHandler(bot_token)
        self.bot = telebot.TeleBot(bot_token)

        @self.bot.message_handler(content_types=['voice'])
        def handle_voice(message):
            try:
                file_id = message.voice.file_id
                chat_id = message.chat.id
                message_id = message.message_id

                ogg_data = self.telegram_handler.download_audio(file_id)
                wav_data = self.telegram_handler.convert_audio_to_wav(ogg_data)
                response = self.speech_recognizer.recognize_speech_from_audio(wav_data)

                if response["success"]:
                    transcription = response["transcription"]
                    hiragana = self.text_converter.convert_to_hiragana(transcription)
                    translation = self.translator_service.translate_text(transcription)

                    self.send_to_telegram(chat_id, message_id, transcription, hiragana, translation)
                else:
                    self.telegram_handler.send_message(chat_id, f"Error: {response['error']}", reply_to_message_id=message_id)
            except Exception as e:
                print(f"An error occurred: {e}")

    def send_to_telegram(self, chat_id, message_id, transcription, hiragana, translation):
        try:
            link = f"[Detailed Parsing](https://ichi.moe/cl/qr/?q={transcription}&r=htr)"
            message = f"You said: {transcription}\nIn Hiragana: {hiragana}\nTranslation: {translation}\n{link}"
            self.telegram_handler.send_message(chat_id, message, reply_to_message_id=message_id)
        except Exception as e:
            print(f"An error occurred while sending message to Telegram: {e}")

    def run(self):
        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception as e:
                print(f"An error occurred during polling: {e}")
                self.bot.stop_polling()


if __name__ == "__main__":
    bot_token = '7499255814:AAH23BW4Bs-l2exd8jv6WODFM1hS1nFlyo8'
    app = SpeechRecognitionApp(bot_token)
    app.run()
