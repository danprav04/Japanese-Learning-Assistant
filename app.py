from flask import Flask
from main import SpeechRecognitionApp
import multiprocessing

app = Flask(__name__)
bot_token = '7499255814:AAH23BW4Bs-l2exd8jv6WODFM1hS1nFlyo8'
bot = SpeechRecognitionApp(bot_token)


def run_bot():
    bot.run()



@app.route('/')
def root():
    return 'Bot is running!'


if __name__ == '__main__':
    bot_process = multiprocessing.Process(target=run_bot)
    bot_process.start()
    app.run()
