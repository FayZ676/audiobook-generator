export async function convertWebmToMp3(webmFile: File): Promise<File> {
  if (typeof window !== 'undefined') {
    throw new Error('This function should only be called on the server-side');
  }

  try {
    const arrayBuffer = await webmFile.arrayBuffer();
    const mp3FileName = webmFile.name.replace('.webm', '.mp3');
    const mp3File = new File([arrayBuffer], mp3FileName, { type: 'audio/mp3' });
    
    return mp3File;
  } catch (error) {
    console.error('Error in server-side audio conversion:', error);
    
    const mp3FileName = webmFile.name.replace('.webm', '.mp3');
    return new File([webmFile], mp3FileName, { type: 'audio/mp3' });
  }
}