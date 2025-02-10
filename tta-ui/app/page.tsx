"use client";

import React, { useState, ChangeEvent } from "react";
import { generate } from "./actions/narration";

export default function Home() {
  const [fileName, setFileName] = useState<string>("");
  const [text, setText] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        setText(e.target?.result as string);
      };
      reader.readAsText(file);
    } else {
      setFileName("");
      setText("");
    }
  }

  async function handleGenerate() {
    setIsLoading(true);
    try {
      const base64String = await generate(text);
      const binaryString = window.atob(base64String);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: "audio/mpeg" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${fileName}.mp3`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Failed to generate narration:", error);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="flex flex-col items-start gap-2 p-4">
      <input
        type="file"
        className="file-input file-input-bordered w-full max-w-xs"
        onChange={handleFileChange}
        disabled={isLoading}
      />
      {fileName && <p className="mt-2">Selected file: {fileName}</p>}
      <button
        className="btn"
        onClick={handleGenerate}
        disabled={!text || isLoading} // Change fileName to text
      >
        {isLoading ? (
          <>
            <span className="loading loading-spinner"></span>
            uploading
          </>
        ) : (
          "Generate"
        )}
      </button>
    </main>
  );
}
