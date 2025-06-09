"use client";

import React from "react";
import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

import { handleRevalidateTag } from "@/app/actions/revalidate";

import pusherClient from "@/app/lib/pusher";

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
  voicesPromise 
}: ScriptClientProps) {
  const router = useRouter();

  const script = use(scriptPromise);

  useEffect(() => {
    const channel = pusherClient.subscribe("script-channel");
    channel.bind("script-update", () => {
      handleRevalidateTag("script");
      router.refresh();
    });

    return () => {
      channel.unbind("script-update");
      pusherClient.unsubscribe("script-channel");
    };
  }, [router]);

  return (
    <div>
      {script ? (
        <ScriptText script={script} />
      ) : (
        <GenerateScriptForm voicesPromise={voicesPromise} />
      )}
    </div>
  );
}
