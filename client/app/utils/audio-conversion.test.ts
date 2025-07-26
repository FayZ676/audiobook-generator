import { describe, it, expect, vi, beforeEach } from 'vitest';
import { convertWebmToMp3 } from '../app/utils/audio-conversion';

// Mock lamejs
vi.mock('lamejs', () => ({
  Mp3Encoder: vi.fn().mockImplementation(() => ({
    encodeBuffer: vi.fn().mockReturnValue(new Int8Array([1, 2, 3, 4])),
    flush: vi.fn().mockReturnValue(new Int8Array([5, 6, 7, 8]))
  }))
}));

// Mock AudioContext
global.AudioContext = vi.fn().mockImplementation(() => ({
  decodeAudioData: vi.fn().mockResolvedValue({
    numberOfChannels: 2,
    sampleRate: 44100,
    getChannelData: vi.fn()
      .mockReturnValueOnce(new Float32Array([0.1, 0.2, 0.3]))
      .mockReturnValueOnce(new Float32Array([0.4, 0.5, 0.6]))
  })
}));

describe('Audio Conversion', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should convert WebM file to MP3', async () => {
    // Create a mock WebM file
    const webmBlob = new Blob(['mock webm data'], { type: 'audio/webm' });
    const webmFile = new File([webmBlob], 'test.webm', { type: 'audio/webm' });

    // Convert to MP3
    const mp3File = await convertWebmToMp3(webmFile);

    // Verify the result
    expect(mp3File).toBeInstanceOf(File);
    expect(mp3File.name).toBe('test.mp3');
    expect(mp3File.type).toBe('audio/mp3');
  });

  it('should handle conversion errors gracefully', async () => {
    // Mock a failed decodeAudioData
    const mockAudioContext = new AudioContext();
    mockAudioContext.decodeAudioData = vi.fn().mockRejectedValue(new Error('Decode failed'));

    const webmBlob = new Blob(['invalid data'], { type: 'audio/webm' });
    const webmFile = new File([webmBlob], 'test.webm', { type: 'audio/webm' });

    await expect(convertWebmToMp3(webmFile)).rejects.toThrow('Failed to convert audio to MP3 format');
  });
});