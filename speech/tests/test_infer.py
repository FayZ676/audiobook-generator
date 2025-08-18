from pathlib import Path

from tta_speech.infer import infer
from tta_speech.inference_types import InferenceParams


def test_infer():
    """Test the infer function by generating audio with faizi_standard voice."""
    test_data_dir = Path(__file__).parent / "data"
    audio_path = str(test_data_dir / "faizi_standard.mp3")
    output_path = str(test_data_dir / "test_output.wav")
    test_text = "[faizi_standard]Hello, this is a test of the text-to-speech system."
    reference_text = "I chase the quiet stories—rooftop gardens at dawn, old songs on street corners. Every question is a doorway to something deeper."

    params = InferenceParams(
        gen_text=test_text,
        voices={
            "faizi_standard": {"ref_audio": audio_path, "ref_text": reference_text}
        },
        vocab_file=str(Path(__file__).parent.parent / "tta_speech" / "vocab.txt"),
        vocoder_name="vocos",
        vocoder_local_path=str(Path(__file__).parent.parent / "tta_speech" / "vocos"),
        load_vocoder_from_local=True,
        remove_silence=False,
        ckpt_file=str(
            Path(__file__).parent.parent
            / "tta_speech"
            / "checkpoints"
            / "model_1250000.safetensors"
        ),
        device="cpu",  # Use CPU for testing to avoid GPU dependencies
    )

    wav_data, sample_rate = infer(params)
    with open(output_path, "wb") as f:
        f.write(wav_data)


if __name__ == "__main__":
    test_infer()
