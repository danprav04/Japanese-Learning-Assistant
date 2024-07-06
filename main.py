import speech_recognition as sr
from googletrans import Translator
from janome.tokenizer import Tokenizer
import jaconv
import keyboard
import tkinter as tk  # Import tkinter for GUI
import winsound  # For Windows beep


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech recorded from `microphone`."""

    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # Adjust the recognizer sensitivity to ambient noise and record audio from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        winsound.Beep(1000, 300)  # Beep when starting to listen
        print("Listening for your input...")
        audio = recognizer.listen(source)

    # Try to recognize the speech in the recording
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio, language="ja-JP")
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response


def convert_to_hiragana(text):
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(text)
    katakana_text = ''.join(token.reading for token in tokens if token.reading)
    hiragana_text = jaconv.kata2hira(katakana_text)
    return hiragana_text


def show_popup(transcription, hiragana, translation):
    root = tk.Tk()
    root.title("Speech Recognition Results")
    root.attributes('-topmost', True)  # Make the window appear on top of all others

    label1 = tk.Label(root, text=f"You said: {transcription}")
    label1.pack()

    label2 = tk.Label(root, text=f"In Hiragana: {hiragana}")
    label2.pack()

    label3 = tk.Label(root, text=f"Translation: {translation}")
    label3.pack()

    root.mainloop()


def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    translator = Translator()

    print("Press F10 to start listening for Japanese input...")
    keyboard.wait('F10')
    print("Say something in Japanese!")
    response = recognize_speech_from_mic(recognizer, microphone)

    if response["success"]:
        transcription = response["transcription"]
        hiragana = convert_to_hiragana(transcription)
        translation = translator.translate(transcription, src='ja', dest='en').text

        show_popup(transcription, hiragana, translation)
    else:
        print("I didn't catch that. Error: {}".format(response["error"]))


if __name__ == "__main__":
    main()
