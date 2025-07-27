"use client";

import React, { useState, useRef, useCallback } from "react";
import { Mic, Square } from "lucide-react";

import Tip from "@/app/components/ui/Tip";

interface AudioRecorderProps {
  onRecordingComplete: (audioFile: File) => void;
  maxDuration?: number; // in seconds
}

export default function AudioRecorder({
  onRecordingComplete,
  maxDuration = 12,
}: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [hasRecording, setHasRecording] = useState(false);

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
      stopTimer();

      // Stop all tracks to release microphone
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
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
          sampleRate: 44100,
        },
      });

      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm;codecs=opus",
        });

        const audioFile = new File(
          [audioBlob],
          `recording-${Date.now()}.webm`,
          { type: "audio/webm;codecs=opus" }
        );

        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        setHasRecording(true);
        onRecordingComplete(audioFile);
      };

      setIsRecording(true);
      setRecordingTime(0);

      // NOTE: Wait 500ms before starting recording to avoid capturing button click
      setTimeout(() => {
        mediaRecorder.start(1000); // NOTE: Collect data every second
        startTimer();
      }, 500);
    } catch (error) {
      console.error("Error starting recording:", error);
      alert(
        "Unable to access microphone. Please check your permissions and try again."
      );
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
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="flex flex-col gap-3 bg-base-100">
      <Tip variant="info">
        <span className="italic font-bold">Read the following:</span> I chase
        the quiet stories—rooftop gardens at dawn, old songs on street corners.
        Every question is a doorway to something deeper.
      </Tip>
      <div className="flex gap-2 flex-wrap">
        {!isRecording && !hasRecording && (
          <button
            onClick={startRecording}
            className="btn btn-primary btn-sm flex-1 min-w-0"
            type="button"
          >
            <Mic className="h-4 w-4" />
            Start Recording
          </button>
        )}

        {isRecording && (
          <button
            onClick={stopRecording}
            className="btn btn-error btn-sm flex-1 min-w-0"
            type="button"
          >
            <Square className="h-4 w-4" />
            Stop Recording
          </button>
        )}

        {hasRecording && !isRecording && (
          <button
            onClick={clearRecording}
            className="btn btn-outline btn-sm flex-1 min-w-0"
            type="button"
          >
            Clear & Re-record
          </button>
        )}
      </div>

      <div className="flex justify-between items-center">
        {isRecording && (
          <div className="flex items-center gap-2 text-sm text-primary">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            Recording...
          </div>
        )}

        <span
          className={`text-sm ${
            recordingTime >= maxDuration - 3
              ? "text-warning"
              : "text-base-content"
          }`}
        >
          {formatTime(recordingTime)} / {formatTime(maxDuration)}
        </span>
      </div>

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
