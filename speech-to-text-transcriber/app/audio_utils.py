import shutil
import subprocess
from pathlib import Path

from app.config import (
    CONVERTIBLE_AUDIO_EXTENSIONS,
    DIRECT_AUDIO_EXTENSIONS,
    FFMPEG_COMMAND,
    TEMP_AUDIO_DIR,
)


def validate_input_file(file_path: str) -> Path:
    if not file_path or not file_path.strip():
        raise ValueError("Audio file path cannot be empty.")

    path = Path(file_path.strip()).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Provided path is not a file: {path}")

    allowed = DIRECT_AUDIO_EXTENSIONS | CONVERTIBLE_AUDIO_EXTENSIONS
    if path.suffix.lower() not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(
            f"Unsupported file format: {path.suffix}. "
            f"Allowed formats are: {allowed_text}"
        )

    return path


def ensure_ffmpeg_installed() -> None:
    if shutil.which(FFMPEG_COMMAND) is None:
        raise RuntimeError(
            "FFmpeg is not installed or not available in PATH. "
            "Install FFmpeg to process MP4/MP3/M4A files."
        )


def prepare_audio_for_transcription(file_path: str) -> Path:
    path = validate_input_file(file_path)
    suffix = path.suffix.lower()

    if suffix in DIRECT_AUDIO_EXTENSIONS:
        return path

    ensure_ffmpeg_installed()

    temp_dir = Path(TEMP_AUDIO_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)

    output_path = temp_dir / f"{path.stem}.wav"

    command = [
        FFMPEG_COMMAND,
        "-y",
        "-i",
        str(path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(output_path),
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"FFmpeg failed to convert file '{path}' to WAV. Details: {exc.stderr}"
        ) from exc

    if not output_path.exists():
        raise RuntimeError("Converted WAV file was not created successfully.")

    return output_path