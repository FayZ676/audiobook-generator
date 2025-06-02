"use client";

import React from "react";
import { useState } from "react";

import { createScript } from "../actions/script";

export default function CreateScriptForm() {
  const [file, setFile] = useState<File | null>(null);
  const [narrator, setNarrator] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  async function handleCreateScript() {
    if (file && narrator) {
      await createScript({ file, narrator });
      setFile(null);
      setNarrator("");
    }
  }

  return (
    <div className="flex flex-col gap-4 max-w-sm">
      <h2>Generate Script</h2>
      <label htmlFor="filename-input">Text File</label>
      <input
        id="file-input"
        name="file"
        type="file"
        accept=".txt"
        onChange={handleFileChange}
        className="border"
      />
      <label htmlFor="narrator-input">Narrator Voice Name</label>
      <input
        id="narrator-input"
        name="narrator"
        type="text"
        className="border"
        value={narrator}
        onChange={(e) => setNarrator(e.target.value)}
      />
      <button
        disabled={!file || !narrator}
        onClick={async () => {
          await handleCreateScript();
        }}
      >
        Submit
      </button>
    </div>
  );
}
