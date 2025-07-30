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
      <h3 className="font-bold">Create New Project</h3>
      <p className="text-sm text-base-content/70">
        First, create a project to organize your audiobook files.
      </p>

      {error && <Tip variant="warning">{error}</Tip>}

      <div className="flex flex-col gap-2">
        <label htmlFor="project-name-input" className="font-medium">
          Project Name
        </label>
        <input
          id="project-name-input"
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
        {isSubmitting ? "Creating Project..." : "Create Project"}
      </button>
    </div>
  );
}
