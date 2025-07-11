"use client";

import React, { useState, use } from "react";
import { Script, getUserScript, deleteScript } from "../../actions/script";
import { Voice } from "../../actions/voices";
import ScriptText from "./ScriptText";

interface ScriptInfo {
  filename: string;
  s3_key: string;
}

interface ScriptListProps {
  scriptsPromise: Promise<ScriptInfo[]>;
  voicesPromise: Promise<Voice[]>;
}

export default function ScriptList({
  scriptsPromise,
  voicesPromise,
}: ScriptListProps) {
  const scripts = use(scriptsPromise);
  const voices = use(voicesPromise);
  const [selectedScript, setSelectedScript] = useState<Script | null>(null);
  const [selectedFilename, setSelectedFilename] = useState<string>("");
  const [isEditing, setIsEditing] = useState(false);
  const [loadingScript, setLoadingScript] = useState<string>("");

  const handleScriptSelect = async (filename: string) => {
    if (selectedFilename === filename) {
      // Collapse if clicking on already selected script
      setSelectedScript(null);
      setSelectedFilename("");
      return;
    }

    setLoadingScript(filename);
    try {
      const script = await getUserScript(filename);
      setSelectedScript(script);
      setSelectedFilename(filename);
    } catch (error) {
      console.error("Error loading script:", error);
    } finally {
      setLoadingScript("");
    }
  };

  const handleDeleteScript = async (filename: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent accordion toggle
    
    if (confirm(`Are you sure you want to delete "${filename}"?`)) {
      try {
        await deleteScript(filename);
        // If this was the selected script, clear it
        if (selectedFilename === filename) {
          setSelectedScript(null);
          setSelectedFilename("");
        }
        // Trigger refresh (you might want to add revalidation here)
        window.location.reload();
      } catch (error) {
        console.error("Error deleting script:", error);
      }
    }
  };

  if (scripts.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        No scripts found. Create your first script to get started.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Your Scripts</h3>
      
      <div className="join join-vertical w-full">
        {scripts.map((scriptInfo) => (
          <div key={scriptInfo.filename} className="collapse collapse-arrow join-item border border-base-300">
            <input 
              type="radio" 
              name="script-accordion" 
              checked={selectedFilename === scriptInfo.filename}
              onChange={() => handleScriptSelect(scriptInfo.filename)}
            />
            <div className="collapse-title text-xl font-medium flex justify-between items-center">
              <span>{scriptInfo.filename}</span>
              <button
                onClick={(e) => handleDeleteScript(scriptInfo.filename, e)}
                className="btn btn-ghost btn-sm text-error hover:bg-error hover:text-error-content"
                title="Delete script"
              >
                🗑️
              </button>
            </div>
            <div className="collapse-content">
              {loadingScript === scriptInfo.filename ? (
                <div className="flex justify-center py-4">
                  <span className="loading loading-spinner loading-md"></span>
                </div>
              ) : selectedScript && selectedFilename === scriptInfo.filename ? (
                <div className="space-y-4">
                  <div className="flex justify-end">
                    <button
                      onClick={() => setIsEditing(!isEditing)}
                      className="btn btn-sm"
                    >
                      {isEditing ? "View Mode" : "Edit Mode"}
                    </button>
                  </div>
                  <ScriptText
                    script={selectedScript}
                    voices={voices}
                    isEditing={isEditing}
                    filename={scriptInfo.filename}
                  />
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}