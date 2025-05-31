import React from "react";
import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

import pusherClient from "@/app/lib/pusher";

import { handleRevalidateTag } from "@/app/actions/revalidate";

import NarrationAudio from "./NarrationAudio";
import NarrationButton from "./NarrationButton";

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

    channel.bind("narration-complete", (data: {}) => {
      handleRevalidateTag("narration");
      router.refresh();
    });

    return () => {
      channel.unbind("narration-completed");
      pusherClient.unsubscribe("narration-channel");
    };
  }, []);

  return (
    <>
      {narrationUrl ? (
        <NarrationAudio narrationUrl={narrationUrl} />
      ) : (
        <NarrationButton />
      )}
    </>
  );
}
