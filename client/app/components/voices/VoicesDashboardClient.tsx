"use client";

import React from "react";
import { useState, use } from "react";
import { useRouter } from "next/navigation";

import { Plus } from "lucide-react";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { getUserSpecificChannels } from "@/app/lib/pusher-channels";
import type { Voice } from "../../actions/voices";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import VoiceAddModal from "./VoiceAddModal";
import VoiceCard from "./VoiceCard";

interface VoicesDashboardClientProps {
  userId: string;
  voicesPromise: Promise<Voice[]>;
}

export default function VoicesDashboardClient({
  userId,
  voicesPromise,
}: VoicesDashboardClientProps) {
  const router = useRouter();
  const voices = use(voicesPromise);
  const userChannels = getUserSpecificChannels(userId);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // TODO: Why does this component need pusher?
  usePusherSubscriptions({
    channels: [userChannels.VOICES_CHANNEL],
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
            <VoiceCard key={voice.name} voice={voice} />
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
