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
      <input
        id="narrator-input"
        name="narrator"
        type="text"
        className="bg-gray-200 p-2 rounded"
        value={narrator}
        onChange={(e) => setNarrator(e.target.value)}
      />
      <button
        disabled={!file || !narrator}
        onClick={async () => {
          await handleCreateScript();
        }}
        className="bg-blue-500 text-white p-2 rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        Build Script
      </button>
    </div>
  );
}
