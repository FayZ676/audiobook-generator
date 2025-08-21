import { useRef, useState } from "react";

interface UseLazyAudioOptions {
  trackTime?: boolean; // Whether to track currentTime and duration
  onPlay?: () => void;
  onPause?: () => void;
  onEnded?: () => void;
  onTimeUpdate?: () => void;
  onLoadedMetadata?: () => void;
}

export function useLazyAudio(
  url: () => Promise<string>,
  options: UseLazyAudioOptions = {}
) {
  const { trackTime = false } = options;
  const audioRef = useRef<HTMLAudioElement>(null);
  const [loaded, setLoaded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Time tracking state (only when trackTime is enabled)
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const handlePlay = async () => {
    if (!audioRef.current) return;

    try {
      setIsLoading(true);
      setError(null);

      // Load audio source if not already loaded
      if (!loaded) {
        const audioUrl = await url();
        audioRef.current.src = audioUrl;
        setLoaded(true);
      }

      // Toggle play/pause
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        await audioRef.current.play();
      }
    } catch (err) {
      console.error("Playback failed:", err);
      setError(err instanceof Error ? err.message : "Playback failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      // Load audio URL if not already loaded
      let audioUrl: string;
      if (loaded && audioRef.current?.src) {
        audioUrl = audioRef.current.src;
      } else {
        audioUrl = await url();
      }

      const link = document.createElement("a");
      link.href = audioUrl;
      link.download = "audio.mp3";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Download failed:", err);
      setError(err instanceof Error ? err.message : "Download failed");
    }
  };

  const seekTo = (time: number) => {
    if (audioRef.current && trackTime) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds) || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Slider handlers (only relevant when trackTime is enabled)
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (trackTime) {
      const newTime = parseFloat(e.target.value);
      seekTo(newTime);
    }
  };

  const handleSliderMouseDown = () => {
    if (trackTime) {
      setIsDragging(true);
    }
  };

  const handleSliderMouseUp = () => {
    if (trackTime) {
      setIsDragging(false);
    }
  };

  // Event handlers
  const handlePlay_Audio = () => {
    setIsPlaying(true);
    options.onPlay?.();
  };

  const handlePause = () => {
    setIsPlaying(false);
    options.onPause?.();
  };

  const handleEnded = () => {
    setIsPlaying(false);
    options.onEnded?.();
  };

  const handleTimeUpdate = () => {
    if (trackTime && audioRef.current && !isDragging) {
      setCurrentTime(audioRef.current.currentTime);
    }
    options.onTimeUpdate?.();
  };

  const handleLoadedMetadata = () => {
    if (trackTime && audioRef.current) {
      setDuration(audioRef.current.duration);
    }
    options.onLoadedMetadata?.();
  };

  const audioEventHandlers = {
    onPlay: handlePlay_Audio,
    onPause: handlePause,
    onEnded: handleEnded,
    onTimeUpdate: handleTimeUpdate,
    onLoadedMetadata: handleLoadedMetadata,
  };

  // Calculate progress for progress bars
  const progress =
    trackTime && duration > 0 ? (currentTime / duration) * 100 : 0;

  return {
    audioRef,
    loaded,
    isPlaying,
    isLoading,
    error,
    // Time-related (always available but only meaningful when trackTime is enabled)
    currentTime: trackTime ? currentTime : 0,
    duration: trackTime ? duration : 0,
    progress: trackTime ? progress : 0,
    // Functions (always available but some only work when trackTime is enabled)
    handlePlay,
    handleDownload,
    formatTime,
    handleSliderChange,
    handleSliderMouseDown,
    handleSliderMouseUp,
    audioEventHandlers,
  };
}
