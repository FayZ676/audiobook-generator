import * as lamejs from 'lamejs';

export async function convertWebmToMp3(webmFile: File): Promise<File> {
  try {
    // Create an audio context for processing
    const audioContext = new AudioContext();
    
    // Read the WebM file as array buffer
    const arrayBuffer = await webmFile.arrayBuffer();
    
    // Decode the audio data
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    
    // Get the audio data as float32 arrays
    const leftChannel = audioBuffer.getChannelData(0);
    const rightChannel = audioBuffer.numberOfChannels > 1 ? audioBuffer.getChannelData(1) : leftChannel;
    
    // Convert to 16-bit PCM
    const sampleRate = audioBuffer.sampleRate;
    const leftPCM = convertFloatToInt16(leftChannel);
    const rightPCM = convertFloatToInt16(rightChannel);
    
    // Initialize MP3 encoder
    const mp3encoder = new lamejs.Mp3Encoder(audioBuffer.numberOfChannels, sampleRate, 128);
    
    const mp3Data: Int8Array[] = [];
    const sampleBlockSize = 1152; // samples per mp3 frame
    
    // Encode in chunks
    for (let i = 0; i < leftPCM.length; i += sampleBlockSize) {
      const leftChunk = leftPCM.subarray(i, i + sampleBlockSize);
      const rightChunk = rightPCM.subarray(i, i + sampleBlockSize);
      
      const mp3buf = mp3encoder.encodeBuffer(leftChunk, rightChunk);
      if (mp3buf.length > 0) {
        mp3Data.push(mp3buf);
      }
    }
    
    // Finalize encoding
    const finalMp3buf = mp3encoder.flush();
    if (finalMp3buf.length > 0) {
      mp3Data.push(finalMp3buf);
    }
    
    // Create the final MP3 blob
    const mp3Blob = new Blob(mp3Data, { type: 'audio/mp3' });
    
    // Create MP3 file with proper name
    const mp3FileName = webmFile.name.replace('.webm', '.mp3');
    const mp3File = new File([mp3Blob], mp3FileName, { type: 'audio/mp3' });
    
    return mp3File;
  } catch (error) {
    console.error('Error converting WebM to MP3:', error);
    throw new Error('Failed to convert audio to MP3 format');
  }
}

function convertFloatToInt16(floatArray: Float32Array): Int16Array {
  const int16Array = new Int16Array(floatArray.length);
  for (let i = 0; i < floatArray.length; i++) {
    // Convert float32 (-1 to 1) to int16 (-32768 to 32767)
    const sample = Math.max(-1, Math.min(1, floatArray[i]));
    int16Array[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
  }
  return int16Array;
}