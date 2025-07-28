"use client";

import React, { useState, use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Script } from "../../actions/script";
import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";

import ScriptControls from "./ScriptControls";
import ScriptText from "./ScriptText";
import GenerateScriptForm from "./GenerateScriptForm";

interface ScriptManagerClientProps {
  scriptPromise: Promise<Script | null>;
  voicesPromise: Promise<Voice[]>;
  narrationUrlPromise: Promise<string | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function ScriptManagerClient({
  scriptPromise,
  voicesPromise,
  narrationUrlPromise,
  jobStatePromise,
}: ScriptManagerClientProps) {
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);

  const script = use(scriptPromise);
  const voices = use(voicesPromise);
  const userChannels = useUserChannels();

  usePusherSubscriptions({
    channels: userChannels ? [userChannels.SCRIPT_CHANNEL] : null,
    onUpdate: () => {
      handleRevalidateTag("script");
      router.refresh();
    },
  });

  if (!script) {
    return <GenerateScriptForm />;
  }

  return (
    <div className="flex flex-col gap-4">
      <ScriptControls
        narrationUrlPromise={narrationUrlPromise}
        scriptPromise={scriptPromise}
        jobStatePromise={jobStatePromise}
        voicesPromise={voicesPromise}
        isEditing={isEditing}
        onEditToggle={setIsEditing}
      />
      <ScriptText script={script} voices={voices} isEditing={isEditing} />
    </div>
  );
}
