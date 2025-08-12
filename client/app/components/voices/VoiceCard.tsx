import React, { useState } from "react";
import { Trash2, LoaderCircle, CirclePlay } from "lucide-react";

import { Voice, deleteVoice, getVoiceAudioUrl } from "../../actions/voices";
import AudioPlayer from "../audio/AudioPlayer";
import { useAudioLoader } from "../../hooks/useAudioLoader";

interface VoiceCardProps {
  voice: Voice;
}

export function isUserCreatedVoice(voice: Voice): boolean {
  return (
    voice.audio_path.includes("/audio/") &&
    !voice.audio_path.startsWith("audio/")
  );
}

export default function VoiceCard({ voice }: VoiceCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const { loadAudio, getUrl, isLoading } = useAudioLoader();

  const isUserCreated = isUserCreatedVoice(voice);
  const voiceUrl = getUrl(voice.name);
  const isLoadingAudio = isLoading(voice.name);

  const handleDelete = async () => {
    if (!isUserCreated) return;

    setIsDeleting(true);
    try {
      await deleteVoice(voice.name);
    } catch (error) {
      console.error("Failed to delete voice:", error);
      alert("Failed to delete voice. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  const loadVoiceAudio = async () => {
    await loadAudio(voice.name, async () => {
      const url = await getVoiceAudioUrl(voice.name);
      if (!url) throw new Error("No audio URL returned");
      return url;
    });
  };

  return (
    <div className="flex justify-between items-center p-2">
      <div className="flex flex-col gap-1">
        <span className="truncate max-w-50">{voice.name}</span>
        <div className="text-xs italic text-gray-500 flex gap-2">
          <span>{voice.gender}</span>
          <span>{voice.age}</span>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {voiceUrl ? (
          <AudioPlayer src={voiceUrl} />
        ) : (
          <button
            onClick={loadVoiceAudio}
            disabled={isLoadingAudio}
            className="btn btn-success btn-outline btn-sm"
            title="Play sample"
          >
            {isLoadingAudio ? (
              <LoaderCircle size={16} className="animate-spin" />
            ) : (
              <CirclePlay size={16} />
            )}
          </button>
        )}
        {isUserCreated && (
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className={`btn btn-sm btn-outline ${
              isDeleting ? "btn-disabled" : "btn-error"
            }`}
            title="Delete voice"
          >
            {isDeleting ? (
              <LoaderCircle size={16} className="animate-spin" />
            ) : (
              <Trash2 size={16} />
            )}
          </button>
        )}
      </div>
    </div>
  );
}
