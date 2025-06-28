"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { VOICES_CHANNEL } from "@/app/lib/pusher-channels";

import { Voice } from "../../actions/voices";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import VoiceCard from "./VoiceCard";

interface VoiceListProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoiceList({ voicesPromise }: VoiceListProps) {
  const router = useRouter();

  const voices = use(voicesPromise);

  usePusherSubscriptions({
    channels: [VOICES_CHANNEL],
    onUpdate: () => {
      handleRevalidateTag("voices");
      router.refresh();
    },
    dependencies: [router],
  });

  return (
    <div className="h-64 overflow-y-scroll bg-base-200 rounded p-4">
      <ul className="grid grid-cols-1 gap-2">
        {voices.map((voice) => (
          <li key={voice.name}>
            <VoiceCard voice={voice} />
          </li>
        ))}
      </ul>
    </div>
  );
}
