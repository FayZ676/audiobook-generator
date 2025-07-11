"use client";

import React from "react";
import { useState } from "react";

import { createScript } from "../../actions/script";

import Tip from "../ui/Tip";

interface GenerateScriptFormProps {}

export default function GenerateScriptForm({}: GenerateScriptFormProps) {
  const [textContent, setTextContent] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];

      try {
        const content = await selectedFile.text();
        setTextContent(content);
      } catch (error) {
        console.error("Error reading file:", error);
        setTextContent("");
      }
    }
  };

  async function handleCreateScript() {
    if (textContent) {
      setIsSubmitting(true);
      try {
        await createScript({ textContent });
        setTextContent("");
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
      <Tip variant="info">Only supporting .txt files.</Tip>
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
