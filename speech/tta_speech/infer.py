class DiaTTS:
    def __init__(self):
        self.model = Dia.from_pretrained(
            "nari-labs/Dia-1.6B-0626", compute_dtype="float16"
        )

    def generate(
        self, text: str, reference_audio: bytes, reference_transcript: str
    ) -> bytes:
        output = self.model.generate(
            reference_transcript + text,
            audio_prompt=reference_audio,
            use_torch_compile=False,
            verbose=True,
            cfg_scale=4.0,
            temperature=1.8,
            top_p=0.90,
            cfg_filter_top_k=50,
        )
        return self.model.save_audio("voice_clone.mp3", output)
