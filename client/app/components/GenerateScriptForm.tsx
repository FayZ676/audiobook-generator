"use client";

import React from "react";
import { useState, Suspense } from "react";

import { createScript } from "../actions/script";
import { Voice } from "../actions/voices";

import NarratorVoiceOptionsDropdown from "./NarratorVoiceOptionsDropdown";
import Tip from "./Tip";

interface GenerateScriptFormProps {
  voicesPromise: Promise<Voice[]>;
}

export default function CreateScriptForm({
  voicesPromise,
}: GenerateScriptFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [narrator, setNarrator] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  async function handleCreateScript() {
    if (file && narrator) {
      setIsSubmitting(true);
      try {
        await createScript({ file, narrator });
        setFile(null);
        setNarrator("");
      } catch (error) {
        console.error("Error creating script:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  return (
    <div className="flex flex-col gap-4 bg-base-200 p-4 rounded">
      <label htmlFor="filename-input" className="font-medium">
        Text File
      </label>
      <Tip variant="info">
        Supporting .txt, .pdf, .epub, .docx files. MOBI support coming soon.
      </Tip>
      <input
        id="file-input"
        name="file"
        type="file"
        accept=".txt,.pdf,.epub,.docx"
        onChange={handleFileChange}
        className="bg-base-300 p-2 rounded"
      />
      <label htmlFor="narrator-input" className="font-medium">
        Narrator Voice Name
      </label>
      <Suspense
        fallback={
          <select className="bg-base-300 p-2 rounded" disabled>
            <option>Loading voices...</option>
          </select>
        }
      >
        <NarratorVoiceOptionsDropdown
          voicesPromise={voicesPromise}
          value={narrator}
          onChange={setNarrator}
          disabled={isSubmitting}
        />
      </Suspense>
      <button
        disabled={!file || !narrator || isSubmitting}
        onClick={async () => {
          await handleCreateScript();
        }}
        className="btn btn-block"
      >
        {isSubmitting ? "Building Script..." : "Build Script"}
      </button>
    </div>
  );
}
