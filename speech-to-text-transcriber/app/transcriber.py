from pathlib import Path
from typing import Any, Optional, cast

import speech_recognition as sr

from app.audio_utils import prepare_audio_for_transcription
from app.config import DEFAULT_LANGUAGE


class SpeechToTextTranscriber:
    def __init__(self, language: str = DEFAULT_LANGUAGE):
        self.language = language
        self.recognizer = sr.Recognizer()

    def _recognize_google(self, audio_data: sr.AudioData) -> str:
        recognizer = cast(Any, self.recognizer)

        if not hasattr(recognizer, "recognize_google"):
            raise RuntimeError(
                "SpeechRecognition installation issue: 'recognize_google' is not available."
            )

        return recognizer.recognize_google(audio_data, language=self.language)

    def transcribe_file(self, file_path: str, save_to: Optional[str] = None) -> str:
        prepared_path = prepare_audio_for_transcription(file_path)

        print(f"[INFO] Using audio file: {prepared_path}")

        try:
            with sr.AudioFile(str(prepared_path)) as source:
                print("[INFO] Reading audio...")
                audio_data = self.recognizer.record(source)
        except Exception as exc:
            raise ValueError(
                f"Could not process audio file '{prepared_path}'. Details: {exc}"
            ) from exc

        print("[INFO] Sending audio for transcription...")
        try:
            text = self._recognize_google(audio_data)
        except sr.UnknownValueError as exc:
            raise ValueError("Speech could not be understood clearly.") from exc
        except sr.RequestError as exc:
            raise RuntimeError(f"Speech recognition service failed: {exc}") from exc

        print("[SUCCESS] Transcription completed.")
        print(f"[TEXT] {text}")

        if save_to:
            output_path = Path(save_to)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(text, encoding="utf-8")
            print(f"[INFO] Transcription saved to: {output_path}")

        return text