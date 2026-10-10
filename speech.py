import os
import tempfile

import pyttsx3


def get_available_voices():
    """Return the voices installed on this computer."""

    engine = pyttsx3.init()

    try:
        voices = engine.getProperty("voices")
        return [
            {
                "id": voice.id,
                "name": voice.name,
                "gender": getattr(voice, "gender", None),
            }
            for voice in voices
        ]
    finally:
        engine.stop()


def text_to_speech(text, gender="Female", rate=165):
    """Convert text to speech and return WAV audio bytes."""

    if not text or not text.strip():
        raise ValueError("There is no text available to speak.")

    engine = pyttsx3.init()

    try:
        voices = engine.getProperty("voices")

        if not voices:
            raise RuntimeError(
                "No speech voices are installed on this computer."
            )

        selected_voice = voices[0]
        wanted_gender = gender.lower()

        for voice in voices:
            name = voice.name.lower()
            metadata_gender = str(getattr(voice, "gender", "")).lower()

            if wanted_gender == "female":
                if (
                    "female" in name
                    or "zira" in name
                    or "heera" in name
                    or "female" in metadata_gender
                ):
                    selected_voice = voice
                    break
            elif wanted_gender == "male":
                if (
                    "male" in name
                    or "david" in name
                    or "mark" in name
                    or "male" in metadata_gender
                ):
                    selected_voice = voice
                    break

        engine.setProperty("voice", selected_voice.id)
        engine.setProperty("rate", rate)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "summary.wav")

            engine.save_to_file(text, output_path)
            engine.runAndWait()
            engine.stop()

            if not os.path.exists(output_path):
                raise RuntimeError("Speech audio could not be generated.")

            with open(output_path, "rb") as audio_file:
                audio_bytes = audio_file.read()

            if not audio_bytes:
                raise RuntimeError("The generated speech file is empty.")

            return audio_bytes
    finally:
        try:
            engine.stop()
        except Exception:
            pass
