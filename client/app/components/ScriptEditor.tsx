import React, { useState, useEffect } from "react";

import { Script, updateScript } from "../actions/script";
import { Voice } from "../actions/voices";
import Tip from "./Tip";

interface ScriptEditorProps {
  script: Script;
  voices: Voice[];
  onSave: () => void;
  onCancel: () => void;
}

export default function ScriptEditor({ script, voices, onSave, onCancel }: ScriptEditorProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Update editing script when script prop changes
  useEffect(() => {
    setEditingScript(script);
  }, [script]);

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  const handleTextChange = (index: number, newText: string) => {
    clearMessages();
    const updatedScript = [...editingScript];
    updatedScript[index] = { ...updatedScript[index], text: newText };
    setEditingScript(updatedScript);
  };

  const handleSpeakerChange = (index: number, voiceName: string) => {
    clearMessages();
    const selectedVoice = voices.find(voice => voice.name === voiceName);
    if (selectedVoice) {
      const updatedScript = [...editingScript];
      updatedScript[index] = {
        ...updatedScript[index],
        voice_name: selectedVoice.name,
        speaker: {
          names: [selectedVoice.name],
          age: selectedVoice.age,
          gender: selectedVoice.gender,
        },
      };
      setEditingScript(updatedScript);
    }
  };

  const handleSave = async () => {
    // Basic validation
    if (editingScript.length === 0) {
      setError("Script cannot be empty");
      return;
    }

    const hasEmptyText = editingScript.some(segment => !segment.text.trim());
    if (hasEmptyText) {
      setError("All script segments must have text");
      return;
    }

    setIsSaving(true);
    clearMessages();
    
    try {
      await updateScript({ script: editingScript });
      setSuccess("Script updated successfully!");
      onSave();
    } catch (error) {
      console.error("Error updating script:", error);
      setError("Failed to update script. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingScript(script);
    clearMessages();
    onCancel();
  };

  // Show error if no voices are available for editing
  if (voices.length === 0) {
    return (
      <div className="bg-base-200 p-4 rounded">
        <Tip variant="warning">
          No voices available for editing. Please add voices first.
        </Tip>
        <button
          onClick={handleCancel}
          className="btn btn-sm btn-secondary mt-2"
        >
          Back to View Mode
        </button>
      </div>
    );
  }

  return (
    <div className="bg-base-200 p-4 rounded">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Edit Script</h3>
        <div className="flex gap-2">
          <button
            onClick={handleCancel}
            className="btn btn-sm btn-secondary"
            disabled={isSaving}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="btn btn-sm btn-primary"
            disabled={isSaving}
          >
            {isSaving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4">
          <Tip variant="warning">{error}</Tip>
        </div>
      )}

      {success && (
        <div className="mb-4">
          <Tip variant="success">{success}</Tip>
        </div>
      )}
      
      <div className="h-[32rem] overflow-y-scroll bg-base-100 p-4 rounded">
        {editingScript.map((scriptSegment, index) => {
          return (
            <div key={index} className="mb-4">
              <div className="flex items-start gap-2">
                <div className="flex flex-col gap-1 min-w-[150px]">
                  <select
                    value={scriptSegment.voice_name}
                    onChange={(e) => handleSpeakerChange(index, e.target.value)}
                    className="select select-sm select-bordered"
                  >
                    {voices.map((voice) => (
                      <option key={voice.name} value={voice.name}>
                        {voice.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex-1">
                  <textarea
                    value={scriptSegment.text}
                    onChange={(e) => handleTextChange(index, e.target.value)}
                    className="textarea textarea-bordered w-full min-h-[80px]"
                    rows={3}
                    placeholder="Enter script text..."
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}