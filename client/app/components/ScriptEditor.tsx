import React, { useState, useEffect, useCallback } from "react";

import { Script, updateScript } from "../actions/script";
import { Voice } from "../actions/voices";
import Tip from "./Tip";

interface ScriptEditorProps {
  script: Script;
  voices: Voice[];
}

export default function ScriptEditor({ script, voices }: ScriptEditorProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    setEditingScript(script);
  }, [script]);

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  const autoSave = useCallback(async (scriptToSave: Script) => {
    if (scriptToSave.length === 0) {
      setError("Script cannot be empty");
      return;
    }

    const hasEmptyText = scriptToSave.some((segment) => !segment.text.trim());
    if (hasEmptyText) {
      setError("All script segments must have text");
      return;
    }

    setIsSaving(true);
    clearMessages();

    try {
      await updateScript({ script: scriptToSave });
      setSuccess("Saved");
      setTimeout(() => setSuccess(null), 2000);
    } catch (error) {
      console.error("Error updating script:", error);
      setError("Failed to save script");
    } finally {
      setIsSaving(false);
    }
  }, []);

  const debouncedAutoSave = useCallback(
    (() => {
      let timeoutId: NodeJS.Timeout;
      return (scriptToSave: Script) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => autoSave(scriptToSave), 1000);
      };
    })(),
    [autoSave]
  );

  const handleTextChange = (index: number, newText: string) => {
    clearMessages();
    const updatedScript = [...editingScript];
    updatedScript[index] = { ...updatedScript[index], text: newText };
    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  const handleSpeakerChange = (index: number, voiceName: string) => {
    clearMessages();
    const selectedVoice = voices.find((voice) => voice.name === voiceName);
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
      debouncedAutoSave(updatedScript);
    }
  };

  return (
    <div className="h-[32rem] overflow-y-scroll bg-base-200 p-4 rounded">
      {(error || success || isSaving) && (
        <div className="mb-4 flex items-center gap-2">
          {isSaving && (
            <span className="loading loading-spinner loading-sm"></span>
          )}
          {error && <Tip variant="warning">{error}</Tip>}
          {success && <Tip variant="success">{success}</Tip>}
        </div>
      )}

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
  );
}
