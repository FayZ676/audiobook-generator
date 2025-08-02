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
  const [showForm, setShowForm] = useState(false);

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
      setShowForm(false);
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

  if (!showForm) {
    return (
      <button
        onClick={() => setShowForm(true)}
        className="btn btn-block"
        disabled={isCreating}
      >
        <Plus className="h-4 w-4" />
        Add Chapter
      </button>
    );
  }

  return (
    <div className="card bg-base-100 shadow-sm border">
      <div className="card-body p-4">
        <h4 className="card-title text-base">Add New Chapter</h4>

        {error && <Tip variant="warning">{error}</Tip>}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="form-control">
            <label className="label">
              <span className="label-text">Chapter Name</span>
            </label>
            <input
              type="text"
              value={chapterName}
              onChange={(e) => setChapterName(e.target.value)}
              placeholder="Chapter 1"
              className="input input-bordered"
              disabled={isCreating}
              autoFocus
            />
          </div>

          <div className="flex gap-2 justify-end">
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setError(null);
                setChapterName("");
              }}
              className="btn btn-ghost btn-sm"
              disabled={isCreating}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary btn-sm"
              disabled={isCreating || !chapterName.trim()}
            >
              {isCreating ? (
                <>
                  <span className="loading loading-spinner loading-xs"></span>
                  Creating...
                </>
              ) : (
                "Create Chapter"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
