# NOTE: Based on this example: https://github.com/nari-labs/dia/blob/main/example/voice_clone.py


from dia.model import Dia


class DiaTTS:
    def __init__(self):
        self.model = Dia.from_pretrained(
            "nari-labs/Dia-1.6B-0626", compute_dtype="float16"
        )

    def generate(
        self,
        text: str,
        reference_audio_path: str,
        reference_audio_transcript: str,
        output_path: str,
    ) -> None:
        """Synthesize the provided `text` using `audio` for instant voice cloning and save output to a provided `output_path`."""
        output_result = self.model.generate(
            reference_audio_transcript + text,
            audio_prompt=reference_audio_path,
            use_torch_compile=False,
            verbose=True,
            cfg_scale=4.0,
            temperature=1.8,
            top_p=0.90,
            cfg_filter_top_k=50,
        )
        return self.model.save_audio(output_path, output_result)  # type: ignore
