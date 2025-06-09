"use client";

import React from "react";
import { useState, Suspense } from "react";

import { createScript } from "../actions/script";
import { Voice } from "../actions/voices";

import NarratorVoiceOptionsDropdown from "./NarratorVoiceOptionsDropdown";

interface GenerateScriptFormProps {
  voicesPromise: Promise<Voice[]>;
}

export default function CreateScriptForm({ voicesPromise }: GenerateScriptFormProps) {
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
    <div className="flex flex-col gap-2 bg-gray-50 p-4 rounded">
      <label htmlFor="filename-input" className="font-medium">
        Text File
      </label>
      <input
        id="file-input"
        name="file"
        type="file"
        accept=".txt"
        onChange={handleFileChange}
        className="bg-gray-200 p-2 rounded"
      />
      <label htmlFor="narrator-input" className="font-medium">
        Narrator Voice Name
      </label>
      <Suspense
        fallback={
          <select className="bg-gray-200 p-2 rounded" disabled>
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
        className="bg-blue-500 text-white p-2 rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {isSubmitting ? "Building Script..." : "Build Script"}
      </button>
    </div>
  );
}
