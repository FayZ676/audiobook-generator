"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";

import { SPEECH_CHANNEL } from "@/app/lib/pusher-channels";

import { handleRevalidateTag } from "@/app/actions/revalidate";

import NarrationAudio from "./NarrationAudio";

interface NarrationClientProps {
  narrationUrlPromise: Promise<string | null>;
}

export default function NarrationClient({
  narrationUrlPromise,
}: NarrationClientProps) {
  const router = useRouter();

  const narrationUrl = use(narrationUrlPromise);

  usePusherSubscriptions({
    channels: [SPEECH_CHANNEL],
    onUpdate: () => {
      handleRevalidateTag("narration");
      router.refresh();
    },
  });

  return <>{narrationUrl && <NarrationAudio narrationUrl={narrationUrl} />}</>;
}
