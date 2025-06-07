"use client";

import React from "react";
import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

import pusherClient from "@/app/lib/pusher";

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

  useEffect(() => {
    const channel = pusherClient.subscribe("narration-channel");
    channel.bind("narration-update", () => {
      handleRevalidateTag("narration");
      router.refresh();
    });

    return () => {
      channel.unbind("narration-update");
      pusherClient.unsubscribe("narration-channel");
    };
  }, [router]);

  return <>{narrationUrl && <NarrationAudio narrationUrl={narrationUrl} />}</>;
}
