"use client";

import React, { useState } from "react";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";

import { createChapter } from "../../actions/chapter";
import Tip from "../ui/Tip";

interface CreateChapterFormProps {
  onChapterCreated?: () => void;
}

export default function CreateChapterForm({
  onChapterCreated,
}: CreateChapterFormProps) {
  const router = useRouter();
  const [chapterName, setChapterName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chapterName.trim()) {
      setError("Chapter name is required");
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      await createChapter({ chapterName: chapterName.trim() });
      const trimmedChapterName = chapterName.trim();
      setChapterName("");
      setIsOpen(false);
      onChapterCreated?.();
      // Navigate to the newly created chapter
      router.push(`/project/${encodeURIComponent(trimmedChapterName)}`);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      setError(errorMessage || "Failed to create chapter");
    } finally {
      setIsCreating(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setError(null);
    setChapterName("");
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="btn btn-block text-gray-500 text-xs"
        disabled={isCreating}
      >
        <Plus className="h-4 w-4" />
        Add Chapter
      </button>

      <div className={`modal ${isOpen ? "modal-open" : ""}`}>
        <div className="modal-box max-w-2xl">
          {error && <Tip variant="warning">{error}</Tip>}

          <div className="flex flex-col gap-2 rounded">
            <input
              name="chapterName"
              type="text"
              value={chapterName}
              onChange={(e) => setChapterName(e.target.value)}
              placeholder="Chapter Name"
              className="bg-base-300 p-2 rounded"
              disabled={isCreating}
              autoFocus
              required
            />
          </div>

          <div className="modal-action">
            <button
              type="submit"
              disabled={isCreating || !chapterName.trim()}
              onClick={handleSubmit}
              className="btn"
            >
              {isCreating ? "Adding ..." : "Add Chapter"}
            </button>
            <button
              onClick={handleClose}
              className="btn btn-ghost"
              disabled={isCreating}
            >
              Cancel
            </button>
          </div>
        </div>
        <div className="modal-backdrop" onClick={handleClose}></div>
      </div>
    </>
  );
}
