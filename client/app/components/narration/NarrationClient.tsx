"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";

import { NARRATION_CHANNEL } from "@/app/lib/pusher-channels";

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
    channels: [NARRATION_CHANNEL],
    onUpdate: () => {
      handleRevalidateTag("narration");
      router.refresh();
    },
    dependencies: [router],
  });

  return <>{narrationUrl && <NarrationAudio narrationUrl={narrationUrl} />}</>;
}
