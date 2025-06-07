"use client";

import React from "react";
import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

import pusherClient from "@/app/lib/pusher";

import { Voice } from "../actions/voices";

import VoiceCard from "./VoiceCard";

interface VoiceListProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoiceList({ voicesPromise }: VoiceListProps) {
  const router = useRouter();
  
  const voices = use(voicesPromise);

  useEffect(() => {
    const channel = pusherClient.subscribe("voice-channel");
    channel.bind("voice-update", () => {
      router.refresh();
    });

    return () => {
      channel.unbind("voice-update");
      pusherClient.unsubscribe("voice-channel");
    };
  }, [router]);
  return (
    <div className="h-64 overflow-y-scroll bg-gray-50 rounded p-4">
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
