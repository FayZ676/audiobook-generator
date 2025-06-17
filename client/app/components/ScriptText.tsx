import React, { useState } from "react";

import { Script, updateScript } from "../actions/script";
import { Voice } from "../actions/voices";

interface ScriptTextProps {
  script: Script;
  voices: Voice[];
}

export default function ScriptText({ script, voices }: ScriptTextProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleTextChange = (index: number, newText: string) => {
    const updatedScript = [...editingScript];
    updatedScript[index] = { ...updatedScript[index], text: newText };
    setEditingScript(updatedScript);
  };

  const handleSpeakerChange = (index: number, voiceName: string) => {
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
    setIsSaving(true);
    try {
      await updateScript({ script: editingScript });
      setIsEditing(false);
    } catch (error) {
      console.error("Error updating script:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingScript(script);
    setIsEditing(false);
  };

  return (
    <div className="bg-base-200 p-4 rounded">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Script</h3>
        <div className="flex gap-2">
          {!isEditing ? (
            <button
              onClick={() => setIsEditing(true)}
              className="btn btn-sm btn-primary"
            >
              Edit Script
            </button>
          ) : (
            <>
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
            </>
          )}
        </div>
      </div>
      
      <div className="h-[32rem] overflow-y-scroll bg-base-100 p-4 rounded">
        {editingScript.map((scriptSegment, index) => {
          return (
            <div key={index} className="mb-4">
              <div className="flex items-start gap-2">
                <div className="flex flex-col gap-1 min-w-[150px]">
                  {isEditing ? (
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
                  ) : (
                    <span
                      className="font-medium tooltip tooltip-right"
                      data-tip={scriptSegment.voice_name}
                    >
                      {scriptSegment.speaker.names[0]}
                    </span>
                  )}
                </div>
                <div className="flex-1">
                  {isEditing ? (
                    <textarea
                      value={scriptSegment.text}
                      onChange={(e) => handleTextChange(index, e.target.value)}
                      className="textarea textarea-bordered w-full min-h-[80px]"
                      rows={3}
                    />
                  ) : (
                    <p>{scriptSegment.text}</p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
