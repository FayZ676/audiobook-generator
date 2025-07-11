"use client";

import React from "react";
import { useState, Suspense } from "react";

import { createScript, Script } from "../../actions/script";
import { Voice } from "../../actions/voices";

import NarratorVoiceOptionsDropdown from "../voices/NarratorVoiceOptionsDropdown";
import Tip from "../ui/Tip";

interface GenerateScriptModalProps {
  isOpen: boolean;
  onClose: () => void;
  voicesPromise: Promise<Voice[]>;
  existingScript?: Script | null;
}

export default function GenerateScriptModal({
  isOpen,
  onClose,
  voicesPromise,
  existingScript,
}: GenerateScriptModalProps) {
  const [textContent, setTextContent] = useState<string>("");
  const [narrator, setNarrator] = useState("");
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
    if (textContent && narrator) {
      setIsSubmitting(true);
      try {
        const characterVoiceMappings =
          existingScript?.speakers.reduce((acc, speaker) => {
            if (speaker.names[0] && speaker.voice_name) {
              acc[speaker.names[0]] = speaker.voice_name;
            }
            return acc;
          }, {} as Record<string, string>) || {};

        await createScript({
          textContent,
          characterVoiceMappings,
        });
        setTextContent("");
        setNarrator("");
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
      setNarrator("");
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
            disabled={!textContent || !narrator || isSubmitting}
            onClick={async () => {
              await handleCreateScript();
            }}
            className="btn btn-primary"
          >
            {isSubmitting ? "Building Script..." : "Build Script"}
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={handleClose}></div>
    </div>
  );
}
