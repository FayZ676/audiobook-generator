import { useEffect, useRef, useState } from "react";

interface UseAudioPlayerOptions {
  disabled?: boolean;
  trackTime?: boolean;
}

export function useAudioPlayer(src: string, options: UseAudioPlayerOptions = {}) {
  const { disabled = false, trackTime = false } = options;
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  // Reset state when src changes
  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;

    setIsPlaying(false);
    setIsLoading(false);
    setError(null);
    setCurrentTime(0);
    setDuration(0);
    el.load();
  }, [src]);

  // Time tracking effect (only when trackTime is true)
  useEffect(() => {
    if (!trackTime) return;
    
    const el = audioRef.current;
    if (!el) return;

    const updateTime = () => {
      if (!isDragging) {
        setCurrentTime(el.currentTime);
      }
    };

    const updateDuration = () => {
      setDuration(el.duration || 0);
    };

    el.addEventListener("timeupdate", updateTime);
    el.addEventListener("loadedmetadata", updateDuration);
    el.addEventListener("durationchange", updateDuration);

    return () => {
      el.removeEventListener("timeupdate", updateTime);
      el.removeEventListener("loadedmetadata", updateDuration);
      el.removeEventListener("durationchange", updateDuration);
    };
  }, [isDragging, trackTime]);

  const play = async () => {
    if (disabled) return;

    const el = audioRef.current;
    if (!el) return;

    try {
      setIsLoading(true);
      setError(null);
      await el.play();
    } catch (err) {
      setError("Failed to play audio");
      console.error("Audio play error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const pause = () => {
    const el = audioRef.current;
    if (!el) return;
    el.pause();
  };

  const togglePlay = async () => {
    if (isPlaying) {
      pause();
    } else {
      await play();
    }
  };

  const seekTo = (time: number) => {
    const el = audioRef.current;
    if (!el) return;
    
    setCurrentTime(time);
    el.currentTime = time;
  };

  const audioEventHandlers = {
    onPlay: () => setIsPlaying(true),
    onPause: () => setIsPlaying(false),
    onEnded: () => setIsPlaying(false),
    onError: () => setError("Audio error"),
  };

  return {
    audioRef,
    isPlaying,
    isLoading,
    error,
    currentTime,
    duration,
    isDragging,
    setIsDragging,
    play,
    pause,
    togglePlay,
    seekTo,
    audioEventHandlers,
  };
}