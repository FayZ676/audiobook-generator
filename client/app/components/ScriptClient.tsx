"use client";

import React from "react";
import { use } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";

import { SCRIPT_CHANNEL } from "@/app/lib/pusher-channels";

import { Script } from "../actions/script";
import { Voice } from "../actions/voices";

import GenerateScriptForm from "./GenerateScriptForm";
import ScriptText from "./ScriptText";

interface ScriptClientProps {
  scriptPromise: Promise<Script | null>;
  voicesPromise: Promise<Voice[]>;
}

export default function ScriptClient({
  scriptPromise,
  voicesPromise,
}: ScriptClientProps) {
  const router = useRouter();

  const script = use(scriptPromise);
  const voices = use(voicesPromise);

  usePusherSubscriptions({
    channels: [SCRIPT_CHANNEL],
    onUpdate: () => {
      handleRevalidateTag("script");
      router.refresh();
    },
    dependencies: [router],
  });

  return (
    <div>
      {script ? (
        <ScriptText script={script} voices={voices} />
      ) : (
        <GenerateScriptForm voicesPromise={voicesPromise} />
      )}
    </div>
  );
}
