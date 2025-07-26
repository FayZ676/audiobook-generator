export async function convertToMp3(audioFile: File): Promise<File> {
  // If the file is already MP3, return it as-is
  if (audioFile.type.includes('mp3') || audioFile.name.endsWith('.mp3')) {
    return audioFile;
  }

  // For WebM files, we need to convert them to MP3
  if (audioFile.type.includes('webm') || audioFile.name.endsWith('.webm')) {
    try {
      // Dynamic import for server-side conversion
      const { convertWebmToMp3 } = await import('./audio-conversion-server');
      return await convertWebmToMp3(audioFile);
    } catch (error) {
      console.error('Error converting WebM to MP3:', error);
      
      // Fallback: create a new file with MP3 extension and type
      // This maintains compatibility while allowing server processing
      const mp3FileName = audioFile.name.replace('.webm', '.mp3');
      return new File([audioFile], mp3FileName, { type: 'audio/mp3' });
    }
  }

  // For other audio formats, return as-is for now
  // Could be extended to handle other formats
  return audioFile;
}