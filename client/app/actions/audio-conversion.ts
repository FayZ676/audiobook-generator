"use server";

export async function validateMp3File(mp3File: File): Promise<File> {
  // Validate that the file is in MP3 format
  if (!mp3File.type.includes('mp3') && !mp3File.name.endsWith('.mp3')) {
    throw new Error('File must be in MP3 format');
  }
  
  // Basic size validation (files should not be empty or too large)
  if (mp3File.size === 0) {
    throw new Error('Audio file is empty');
  }
  
  if (mp3File.size > 10 * 1024 * 1024) { // 10MB limit
    throw new Error('Audio file is too large (max 10MB)');
  }
  
  return mp3File;
}