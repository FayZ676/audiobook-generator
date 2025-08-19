"use client";

import React, { useState } from "react";
import { createProject } from "../../actions/project";
import Tip from "../ui/Tip";

export default function CreateProjectForm() {
  const [projectName, setProjectName] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCreateProject() {
    if (projectName.trim()) {
      setIsSubmitting(true);
      setError(null);
      try {
        await createProject({ projectName: projectName.trim() });
        setProjectName("");
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
      <h4 className="mt-0 mb-0">Create New Project</h4>

      {error && <Tip variant="warning">{error}</Tip>}

      <div className="flex flex-col gap-2">
        <input
          type="text"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          placeholder="Enter project name..."
          className="input input-bordered w-full"
          disabled={isSubmitting}
        />
      </div>

      <button
        disabled={!projectName.trim() || isSubmitting}
        onClick={handleCreateProject}
        className="btn btn-primary"
      >
        {isSubmitting ? "Creating Project..." : "Create"}
      </button>
    </div>
  );
}
