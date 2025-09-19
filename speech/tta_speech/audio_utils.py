import os

from pydub import AudioSegment


def concat_audio_from_files(
    file_paths: list[str], audio_format: str = "wav", save_dir: str = "/tmp"
) -> str:
    """Concatenate MP3 files from local file paths and save to save_dir."""
    combined = AudioSegment.empty()
    for file_path in file_paths:
        seg = AudioSegment.from_file(file_path, format=audio_format)
        combined += seg

    os.makedirs(save_dir, exist_ok=True)
    output_path = os.path.join(save_dir, "concatenated_audio.mp3")
    combined.export(output_path, format="mp3")
    return output_path
