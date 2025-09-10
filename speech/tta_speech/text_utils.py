from tta_types.types import SpeechRequestSegment


def compute_word_count(text_segments: list[SpeechRequestSegment]):
    return sum(len(segment.text.split()) for segment in text_segments)
