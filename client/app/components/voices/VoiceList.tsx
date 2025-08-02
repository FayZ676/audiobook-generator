"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";

import { Voice } from "../../actions/voices";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import VoiceCard from "./VoiceCard";

interface VoiceListProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoiceList({ voicesPromise }: VoiceListProps) {
  const router = useRouter();
  const voices = use(voicesPromise);
  const userChannels = useUserChannels();

  usePusherSubscriptions({
    channels: userChannels ? [userChannels.VOICES_CHANNEL] : null,
    onUpdate: () => {
      handleRevalidateTag("voices");
      router.refresh();
    },
  });

  return (
    voices.length > 0 && (
      <div className="max-h-80 overflow-y-scroll">
        {voices.map((voice) => (
          <VoiceCard key={voice.name} voice={voice} />
        ))}
      </div>
    )
  );
}
