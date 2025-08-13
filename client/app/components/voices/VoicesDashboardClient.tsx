"use client";

import React from "react";
import { useState, use } from "react";
import { useRouter } from "next/navigation";

import { Plus } from "lucide-react";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";

import { Voice } from "../../actions/voices";
import { VoiceAudioData } from "@/app/types";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import VoiceAddModal from "./VoiceAddModal";
import VoiceCard from "./VoiceCard";

interface VoicesDashboardClientProps {
  voicesPromise: Promise<Voice[]>;
  voiceAudioData: VoiceAudioData;
}

export default function VoicesDashboardClient({
  voicesPromise,
  voiceAudioData,
}: VoicesDashboardClientProps) {
  const router = useRouter();
  const voices = use(voicesPromise);
  const userChannels = useUserChannels();
  const [isModalOpen, setIsModalOpen] = useState(false);

  usePusherSubscriptions({
    channels: userChannels ? [userChannels.VOICES_CHANNEL] : null,
    onUpdate: async () => {
      await handleRevalidateTag("voices");
      router.refresh();
    },
  });

  return (
    <div className="flex flex-col gap-2 w-full">
      <h4>Voices</h4>
      {voices.length > 0 && (
        <div className="flex flex-col max-h-80 overflow-y-scroll">
          {voices.map((voice) => (
            <VoiceCard
              key={voice.name}
              voice={voice}
              voiceAudioUrl={voiceAudioData.urls[voice.name]}
            />
          ))}
        </div>
      )}
      <button
        onClick={() => setIsModalOpen(true)}
        className="btn btn-block mt-4 text-gray-500"
      >
        <Plus className="h-4 w-4" />
        Add Voice
      </button>
      <VoiceAddModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
