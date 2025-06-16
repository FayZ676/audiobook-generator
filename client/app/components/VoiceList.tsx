"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { VOICES_CHANNEL } from "@/app/lib/pusher-channels";

import { Voice } from "../actions/voices";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import VoiceCard from "./VoiceCard";

interface VoiceListProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoiceList({ voicesPromise }: VoiceListProps) {
  const router = useRouter();

  const voices = use(voicesPromise);

  console.log('🎤 VoiceList component mounted, listening for pusher events on:', VOICES_CHANNEL);

  usePusherSubscriptions({
    channels: [VOICES_CHANNEL],
    onUpdate: (channel, event, data) => {
      console.log(`🔔 VoiceList received pusher update - Channel: "${channel}", Event: "${event}"`, data);
      console.log('🔄 VoiceList calling handleRevalidateTag("voices")...');
      handleRevalidateTag("voices");
      console.log('🔄 VoiceList calling router.refresh()...');
      router.refresh();
      console.log('✅ VoiceList refresh completed');
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
