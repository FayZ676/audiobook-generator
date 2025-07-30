"use client";

import React, { useState, use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Script } from "../../actions/script";
import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";

import ScriptControls from "../script/ScriptControls";
import ScriptText from "../script/ScriptText";
import GenerateScriptForm from "../script/GenerateScriptForm";
import CreateProjectForm from "./CreateProjectForm";

interface ProjectManagerClientProps {
  scriptPromise: Promise<Script | null>;
  voicesPromise: Promise<Voice[]>;
  narrationUrlPromise: Promise<string | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  projectPromise: Promise<{ name: string; created_at: string } | null>;
}

export default function ProjectManagerClient({
  scriptPromise,
  voicesPromise,
  narrationUrlPromise,
  jobStatePromise,
  projectPromise,
}: ProjectManagerClientProps) {
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);

  const script = use(scriptPromise);
  const voices = use(voicesPromise);
  const project = use(projectPromise);
  const userChannels = useUserChannels();

  usePusherSubscriptions({
    channels: userChannels ? [userChannels.SCRIPT_CHANNEL] : null,
    onUpdate: () => {
      handleRevalidateTag("script");
      handleRevalidateTag("project");
      router.refresh();
    },
  });

  if (!project) {
    return <CreateProjectForm />;
  }

  if (!script) {
    return (
      <div className="flex flex-col gap-4">
        <div className="bg-base-200 p-4 rounded">
          <h3 className="font-bold">Project: {project.name}</h3>
          <p className="text-sm text-base-content/70">
            Created: {new Date(project.created_at).toLocaleDateString()}
          </p>
        </div>
        <GenerateScriptForm />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="bg-base-200 p-4 rounded">
        <h3 className="font-bold">Project: {project.name}</h3>
        <p className="text-sm text-base-content/70">
          Created: {new Date(project.created_at).toLocaleDateString()}
        </p>
      </div>

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
