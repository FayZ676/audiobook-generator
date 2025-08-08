"use client";

import React from "react";
import { useState } from "react";

import { createScript } from "../../actions/script";

import Tip from "../ui/Tip";

interface GenerateScriptFormProps {
  chapterName: string;
}

export default function GenerateScriptForm({
  chapterName,
}: GenerateScriptFormProps) {
  const [textContent, setTextContent] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];

      try {
        const content = await selectedFile.text();
        setTextContent(content);
        setError(null);
      } catch (error) {
        setTextContent("");
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        setError(errorMessage ? errorMessage : "Something went wrong.");
      }
    }
  };

  async function handleCreateScript() {
    if (textContent) {
      setIsSubmitting(true);
      setError(null);
      try {
        await createScript({ textContent, chapterName });
        setTextContent("");
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        setError(errorMessage ? errorMessage : "Something went wrong.");
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  return (
    <div className="flex flex-col gap-4 bg-base-200 p-4 rounded">
      <label htmlFor="filename-input" className="font-medium">
        Upload Text
      </label>
      <Tip variant="info">Only files with .txt extensions are supported.</Tip>
      {error && <Tip variant="warning">{error}</Tip>}
      <input
        id="file-input"
        name="file"
        type="file"
        accept=".txt"
        onChange={handleFileChange}
        className="bg-base-300 p-2 rounded"
      />
      <button
        disabled={!textContent || isSubmitting}
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
