"use client";

import React from "react";
import { useState } from "react";

import { createScript, Script } from "../../actions/script";

import Tip from "../ui/Tip";

interface GenerateScriptModalProps {
  isOpen: boolean;
  onClose: () => void;
  existingScript?: Script | null;
}

export default function GenerateScriptModal({
  isOpen,
  onClose,
  existingScript,
}: GenerateScriptModalProps) {
  const [textContent, setTextContent] = useState<string>("");
  const [filename, setFilename] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const extractCharacterVoiceMappings = (script: Script) => {
    const mappings: Record<string, string> = {};
    script.speakers.forEach((speaker) => {
      speaker.names.forEach((name) => {
        mappings[name] = speaker.voice_name;
      });
    });
    return mappings;
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];

      try {
        const content = await selectedFile.text();
        setTextContent(content);
        
        // Extract filename without extension
        const fileNameWithoutExt = selectedFile.name.replace(/\.[^/.]+$/, "");
        setFilename(fileNameWithoutExt);
      } catch (error) {
        console.error("Error reading file:", error);
        setTextContent("");
        setFilename("");
      }
    }
  };

  async function handleCreateScript() {
    if (textContent && filename) {
      setIsSubmitting(true);
      try {
        await createScript({ 
          textContent, 
          filename,
          characterVoiceMappings: existingScript ? extractCharacterVoiceMappings(existingScript) : undefined
        });
        setTextContent("");
        setFilename("");
        onClose();
      } catch (error) {
        console.error("Error creating script:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  const handleClose = () => {
    if (!isSubmitting) {
      setTextContent("");
      setFilename("");
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        <h3 className="font-bold text-lg mb-4">
          {existingScript ? "Add New Chapter" : "Generate Script"}
        </h3>

        <div className="flex flex-col gap-4">
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
            disabled={isSubmitting}
          />
        </div>

        <div className="modal-action">
          <button
            onClick={handleClose}
            className="btn btn-ghost"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            disabled={!textContent || !filename || isSubmitting}
            onClick={async () => {
              await handleCreateScript();
            }}
            className="btn"
          >
            {isSubmitting ? "Building Script..." : "Build Script"}
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={handleClose}></div>
    </div>
  );
}
