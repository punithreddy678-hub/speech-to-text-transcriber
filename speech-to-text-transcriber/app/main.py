from app.config import DEFAULT_OUTPUT_FILE
from app.transcriber import SpeechToTextTranscriber


def run_app() -> None:
    print("=== Speech-to-Text Transcriber ===")
    print("Supported formats: .wav, .aiff, .aif, .flac")
    print("Microphone mode is disabled in this version.\n")

    file_path = input("Enter audio file path: ").strip()

    transcriber = SpeechToTextTranscriber()

    try:
        text = transcriber.transcribe_file(
            file_path=file_path,
            save_to=DEFAULT_OUTPUT_FILE
        )
        print("\n=== Final Transcription ===")
        print(text)
    except Exception as error:
        print(f"[ERROR] {error}")