import numpy as np


def create_silence(sample_rate: int, duration_seconds: float) -> np.ndarray:
    """Creates a numpy array of silence for the specified duration."""
    num_samples = int(sample_rate * duration_seconds)
    return np.zeros(num_samples, dtype=np.float32)
