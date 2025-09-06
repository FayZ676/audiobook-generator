import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Trash2, LoaderCircle } from "lucide-react";

import { Voice, deleteVoice, getVoiceAudioUrl } from "../../actions/voices";
import AudioPlayer from "../audio/AudioPlayer";

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
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const isUserCreated = isUserCreatedVoice(voice);

  const handleDelete = async () => {
    if (!isUserCreated) return;

    setIsDeleting(true);
    try {
      await deleteVoice(voice.name);
      router.refresh();
    } catch (error) {
      console.error("Failed to delete voice:", error);
      alert("Failed to delete voice. Please try again.");
    } finally {
      setIsDeleting(false);
    }
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
        <AudioPlayer url={() => getVoiceAudioUrl(voice.name)} />
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
