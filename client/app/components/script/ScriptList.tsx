"use client";

import React, { useState, use } from "react";
import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";
import ScriptItem from "./ScriptItem";

interface ScriptInfo {
  filename: string;
  s3_key: string;
}

interface ScriptListProps {
  scriptsPromise: Promise<ScriptInfo[]>;
  voicesPromise: Promise<Voice[]>;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function ScriptList({
  scriptsPromise,
  voicesPromise,
  jobStatePromise,
}: ScriptListProps) {
  const scripts = use(scriptsPromise);
  const voices = use(voicesPromise);
  const jobState = use(jobStatePromise);
  const [selectedFilename, setSelectedFilename] = useState<string>("");

  const handleScriptSelect = (filename: string) => {
    setSelectedFilename(filename);
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  if (scripts.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No scripts found. Create your first script to get started.
      </div>
    );
  }

  return (
    <div className="join join-vertical w-full">
      {scripts.map((scriptInfo) => (
        <div
          key={scriptInfo.filename}
          className="collapse collapse-arrow join-item border border-base-300"
        >
          <input
            type="radio"
            name="script-accordion"
            checked={selectedFilename === scriptInfo.filename}
            onChange={() => handleScriptSelect(scriptInfo.filename)}
          />
          <ScriptItem
            scriptInfo={scriptInfo}
            voices={voices}
            jobState={jobState}
            isSelected={selectedFilename === scriptInfo.filename}
            onRefresh={handleRefresh}
          />
        </div>
      ))}
    </div>
  );
}
