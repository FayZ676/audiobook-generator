import ffmpeg from 'fluent-ffmpeg';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

export async function convertWebmToMp3(webmFile: File): Promise<File> {
  if (typeof window !== 'undefined') {
    throw new Error('This function should only be called on the server-side');
  }

  let tempInputPath: string | null = null;
  let tempOutputPath: string | null = null;

  try {
    const tempDir = os.tmpdir();
    const uniqueId = Math.random().toString(36).substring(7);
    tempInputPath = path.join(tempDir, `input_${uniqueId}.webm`);
    tempOutputPath = path.join(tempDir, `output_${uniqueId}.mp3`);

    const arrayBuffer = await webmFile.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    await fs.writeFile(tempInputPath, buffer);

    await new Promise<void>((resolve, reject) => {
      ffmpeg(tempInputPath)
        .toFormat('mp3')
        .audioCodec('libmp3lame')
        .audioBitrate(128)
        .on('end', () => resolve())
        .on('error', (err) => reject(err))
        .save(tempOutputPath!);
    });

    const mp3Buffer = await fs.readFile(tempOutputPath);
    const mp3FileName = webmFile.name.replace(/\.webm$/, '.mp3');
    const mp3File = new File([mp3Buffer], mp3FileName, { type: 'audio/mp3' });

    return mp3File;
  } catch (error) {
    console.error('Error in server-side audio conversion:', error);
    
    const mp3FileName = webmFile.name.replace(/\.webm$/, '.mp3');
    return new File([webmFile], mp3FileName, { type: 'audio/mp3' });
  } finally {
    try {
      if (tempInputPath) await fs.unlink(tempInputPath);
      if (tempOutputPath) await fs.unlink(tempOutputPath);
    } catch (cleanupError) {
      console.error('Error cleaning up temporary files:', cleanupError);
    }
  }
}