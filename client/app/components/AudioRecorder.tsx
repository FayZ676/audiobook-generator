import React, { useState, useRef, useCallback } from "react";
import { Mic, Square, Play, Pause } from "lucide-react";
import { convertWebmToMp3 } from "../utils/audio-conversion";

interface AudioRecorderProps {
  onRecordingComplete: (audioFile: File) => void;
  maxDuration?: number; // in seconds
}

export default function AudioRecorder({ 
  onRecordingComplete, 
  maxDuration = 12 
}: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [hasRecording, setHasRecording] = useState(false);
  const [isConverting, setIsConverting] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      stopTimer();
      
      // Stop all tracks to release microphone
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    }
  }, [isRecording, stopTimer]);

  const startTimer = useCallback(() => {
    timerRef.current = setInterval(() => {
      setRecordingTime((prevTime) => {
        const newTime = prevTime + 1;
        if (newTime >= maxDuration) {
          stopRecording();
          return maxDuration;
        }
        return newTime;
      });
    }, 1000);
  }, [maxDuration, stopRecording]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: 'audio/webm;codecs=opus' 
        });
        
        const webmFile = new File(
          [audioBlob], 
          `recording-${Date.now()}.webm`, 
          { type: 'audio/webm;codecs=opus' }
        );

        try {
          setIsConverting(true);
          
          // Convert WebM to MP3
          const mp3File = await convertWebmToMp3(webmFile);
          
          const url = URL.createObjectURL(mp3File);
          setAudioUrl(url);
          setHasRecording(true);
          onRecordingComplete(mp3File);
        } catch (error) {
          console.error('Error converting audio to MP3:', error);
          alert('Failed to convert audio to MP3. Please try again.');
        } finally {
          setIsConverting(false);
        }
      };

      mediaRecorder.start(1000); // Collect data every second
      setIsRecording(true);
      setIsPaused(false);
      setRecordingTime(0);
      startTimer();
      
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Unable to access microphone. Please check your permissions and try again.');
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      stopTimer();
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      startTimer();
    }
  };

  const clearRecording = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioUrl(null);
    setHasRecording(false);
    setRecordingTime(0);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col gap-3 p-3 border border-base-300 rounded bg-base-100">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Audio Recorder</span>
        <span className={`text-sm ${recordingTime >= maxDuration - 3 ? 'text-warning' : 'text-base-content'}`}>
          {formatTime(recordingTime)} / {formatTime(maxDuration)}
        </span>
      </div>

      <div className="flex items-center gap-2">
        {!isRecording && !hasRecording && !isConverting && (
          <button
            onClick={startRecording}
            className="btn btn-primary btn-sm"
            type="button"
          >
            <Mic className="h-4 w-4" />
            Start Recording
          </button>
        )}

        {isRecording && (
          <>
            {!isPaused ? (
              <button
                onClick={pauseRecording}
                className="btn btn-warning btn-sm"
                type="button"
              >
                <Pause className="h-4 w-4" />
                Pause
              </button>
            ) : (
              <button
                onClick={resumeRecording}
                className="btn btn-success btn-sm"
                type="button"
              >
                <Play className="h-4 w-4" />
                Resume
              </button>
            )}
            
            <button
              onClick={stopRecording}
              className="btn btn-error btn-sm"
              type="button"
            >
              <Square className="h-4 w-4" />
              Stop
            </button>
          </>
        )}

        {hasRecording && !isRecording && !isConverting && (
          <button
            onClick={clearRecording}
            className="btn btn-ghost btn-sm"
            type="button"
          >
            Clear & Re-record
          </button>
        )}
      </div>

      {(isRecording || isConverting) && (
        <div className="flex items-center gap-2 text-sm text-primary">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          {isConverting ? 'Converting to MP3...' : isPaused ? 'Recording paused' : 'Recording...'}
        </div>
      )}

      {audioUrl && (
        <div className="mt-2">
          <audio controls className="w-full h-8">
            <source src={audioUrl} />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
}