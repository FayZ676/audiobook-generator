import React, { useState } from "react";
import { Trash2, LoaderCircle } from "lucide-react";

import { Voice, deleteVoice } from "../../actions/voices";
import VoiceAudio from "./VoiceAudio";

interface VoiceCardProps {
  voice: Voice;
}

export function isUserCreatedVoice(voice: Voice): boolean {
  // User-created voices have audio paths like "user_id/audio/voice.mp3"
  // System voices have audio paths like "audio/voice.mp3"
  return (
    voice.audio_path.includes("/audio/") &&
    !voice.audio_path.startsWith("audio/")
  );
}

export default function VoiceCard({ voice }: VoiceCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const isUserCreated = isUserCreatedVoice(voice);

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

  return (
    <div className="flex justify-between items-center">
      <span className="font-small truncate max-w-24">{voice.name}</span>
      <div className="flex ml-auto gap-4 text-sm text-gray-600 items-center">
        <span>{voice.gender === "male" ? "M" : "F"}</span>
        <span>
          {voice.age === "middle-aged"
            ? "MA"
            : voice.age === "young"
            ? "Y"
            : "O"}
        </span>
        <div className="flex items-center gap-2">
          <VoiceAudio voiceName={voice.name} />
          {isUserCreated && (
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className={`btn btn-xs ${
                isDeleting ? "btn-disabled" : "btn-error"
              }`}
              title="Delete voice"
            >
              {isDeleting ? (
                <LoaderCircle size={14} className="animate-spin" />
              ) : (
                <Trash2 size={14} />
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
