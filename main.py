import speech_recognition as sr
import jaconv
from googletrans import Translator


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech recorded from `microphone`."""

    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # Adjust the recognizer sensitivity to ambient noise and record audio from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
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


def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    translator = Translator()

    print("Say something in Japanese!")
    response = recognize_speech_from_mic(recognizer, microphone)

    if response["success"]:
        transcription = response["transcription"]
        hiragana = jaconv.kata2hira(jaconv.kata2hira(jaconv.hira2kata(transcription)))
        translation = translator.translate(transcription, src='ja', dest='en').text

        print("You said: {}".format(transcription))
        print("In Hiragana: {}".format(hiragana))
        print("Translation: {}".format(translation))
    else:
        print("I didn't catch that. Error: {}".format(response["error"]))


if __name__ == "__main__":
    main()
