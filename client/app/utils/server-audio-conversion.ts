export async function convertToMp3(audioFile: File): Promise<File> {
  if (audioFile.type.includes('mp3') || audioFile.name.endsWith('.mp3')) {
    return audioFile;
  }

  if (audioFile.type.includes('webm') || audioFile.name.endsWith('.webm')) {
    try {
      const { convertWebmToMp3 } = await import('./audio-conversion-server');
      return await convertWebmToMp3(audioFile);
    } catch (error) {
      console.error('Error converting WebM to MP3:', error);
      
      const mp3FileName = audioFile.name.replace('.webm', '.mp3');
      return new File([audioFile], mp3FileName, { type: 'audio/mp3' });
    }
  }

  return audioFile;
}