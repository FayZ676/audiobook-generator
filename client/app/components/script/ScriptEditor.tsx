"use client";

import React, { useState, useEffect, useMemo } from "react";

import { Script, updateScript } from "@/app/actions/script";
import { Voice } from "@/app/actions/voices";
import Tip from "@/app/components/ui/Tip";
import CharacterVoiceMapping from "./CharacterVoiceMapping";
import AudioPlayer from "@/app/components/audio/AudioPlayer";
import { getSegmentAudioUrl, regenerateSegment } from "@/app/actions/segments";
import { RotateCw, LoaderCircle, CirclePlay } from "lucide-react";
import { useAudioLoader } from "../../hooks/useAudioLoader";

interface ScriptEditorProps {
  script: Script;
  voices: Voice[];
  chapterName: string;
  processingSegmentIds?: string[];
  playableSegmentIds?: string[];
}

export default function ScriptEditor({
  script,
  voices,
  chapterName,
  processingSegmentIds,
  playableSegmentIds = [],
}: ScriptEditorProps) {
  const [editingScript, setEditingScript] = useState<Script>(script);
  const [regenerating, setRegenerating] = useState<Record<string, boolean>>({});
  const { loadAudio, getUrl, isLoading } = useAudioLoader();

  useEffect(() => {
    setEditingScript(script);
  }, [script]);

  const processingSet = useMemo(
    () => new Set(processingSegmentIds || []),
    [processingSegmentIds]
  );
  const playableSet = useMemo(
    () => new Set(playableSegmentIds || []),
    [playableSegmentIds]
  );

  const loadSegmentUrl = async (segmentId: string) => {
    await loadAudio(segmentId, () =>
      getSegmentAudioUrl(chapterName, segmentId)
    );
  };

  const clearMessages = () => {};

  const autoSave = async (scriptToSave: Script) => {
    if (scriptToSave.segments.length === 0) {
      return;
    }

    const hasEmptyText = scriptToSave.segments.some(
      (segment) => !segment.text.trim()
    );
    if (hasEmptyText) {
      return;
    }

    clearMessages();

    try {
      await updateScript({ script: scriptToSave, chapterName });
    } catch (error) {
      console.error("Error updating script:", error);
    }
  };

  const debouncedAutoSave = (() => {
    let timeoutId: NodeJS.Timeout;
    return (scriptToSave: Script) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => autoSave(scriptToSave), 1000);
    };
  })();

  const handleTextChange = (index: number, newText: string) => {
    clearMessages();
    const updatedSegments = [...editingScript.segments];
    updatedSegments[index] = { ...updatedSegments[index], text: newText };
    const updatedScript = { ...editingScript, segments: updatedSegments };
    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  const handleSegmentCharacterChange = (
    segmentIndex: number,
    characterName: string
  ) => {
    clearMessages();
    const updatedSegments = [...editingScript.segments];
    updatedSegments[segmentIndex] = {
      ...updatedSegments[segmentIndex],
      speaker_alias: characterName,
    };

    const updatedScript = { ...editingScript, segments: updatedSegments };
    setEditingScript(updatedScript);
    debouncedAutoSave(updatedScript);
  };

  const getAllCharacters = () =>
    editingScript.speakers
      .flatMap((speaker) => speaker.character.names)
      .filter((name) => name?.trim())
      .sort();

  const availableCharacters = getAllCharacters();

  const handleRegenerate = async (segmentId: string) => {
    try {
      setRegenerating((prev) => ({ ...prev, [segmentId]: true }));
      await regenerateSegment(chapterName, segmentId);
    } catch (e) {
      console.error("Failed to regenerate segment", e);
    } finally {
      // keep local true until pusher refresh clears via processingSegmentIds update
      // but safe to set false as isRegenerating is union with processingSet
      setRegenerating((prev) => ({ ...prev, [segmentId]: false }));
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <Tip>
        Edit the script text, choose voices for characters, and save changes.
      </Tip>

      <CharacterVoiceMapping
        script={editingScript}
        voices={voices}
        onCharacterVoiceChange={(characterName, voiceName) => {
          const voice = voices.find((v) => v.name === voiceName) || null;
          const create = (
            name: string,
            v: typeof voice,
            age: "young" | "middle-aged" | "old",
            gender: "male" | "female"
          ) => ({
            character: { names: [name], age, gender },
            voice: {
              name: v?.name || "",
              age: v?.age || age,
              gender: v?.gender || gender,
              audio_path: v?.audio_path || "",
              audio_transcript: v?.audio_transcript || "",
            },
          });
          const updatedSpeakers = editingScript.speakers.map((s) =>
            s.character.names.includes(characterName)
              ? create(
                  characterName,
                  voice,
                  s.character.age,
                  s.character.gender
                )
              : s
          );
          const updatedScript = { ...editingScript, speakers: updatedSpeakers };
          setEditingScript(updatedScript);
          debouncedAutoSave(updatedScript);
        }}
        onAddCharacter={(character) => {
          const exists = editingScript.speakers.find((s) =>
            s.character.names.includes(character.name)
          );
          if (!exists) {
            const newSpeaker = {
              character: {
                names: [character.name],
                age: character.age,
                gender: character.gender,
              },
              voice: {
                name: "",
                age: character.age,
                gender: character.gender,
                audio_path: "",
                audio_transcript: "",
              },
            };
            const updatedScript = {
              ...editingScript,
              speakers: [...editingScript.speakers, newSpeaker],
            };
            setEditingScript(updatedScript);
            debouncedAutoSave(updatedScript);
          }
        }}
      />

      <div className="h-[28rem] overflow-y-scroll bg-base-200 p-4 rounded">
        {editingScript.segments.map((scriptSegment, index) => {
          const speaker = editingScript.speakers.find((s) =>
            s.character.names.includes(scriptSegment.speaker_alias)
          );
          const characterName =
            speaker?.character.names[0] || scriptSegment.speaker_alias;
          const voiceName = speaker?.voice.name || "";
          const segmentId = scriptSegment.id as string | undefined;
          const hasAudio = segmentId ? playableSet.has(segmentId) : false;
          const isRegenerating = segmentId
            ? !!regenerating[segmentId] || processingSet.has(segmentId)
            : false;
          const segmentUrl = segmentId ? getUrl(segmentId) : undefined;
          const isLoadingUrl = segmentId ? isLoading(segmentId) : false;

          return (
            <div
              key={index}
              className={`mb-4 ${isRegenerating ? "opacity-80" : ""}`}
            >
              <div className="flex flex-col gap-2">
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={characterName}
                    onChange={(e) =>
                      handleSegmentCharacterChange(index, e.target.value)
                    }
                    className="select select-sm select-bordered min-w-[120px]"
                    disabled={isRegenerating}
                  >
                    {availableCharacters.map((char) => (
                      <option key={char} value={char}>
                        {char}
                      </option>
                    ))}
                  </select>
                  <div className="ml-auto flex items-center gap-3">
                    <span className="text-sm text-gray-500 italic">
                      {voiceName}
                    </span>
                    {isRegenerating && (
                      <span className="badge badge-warning badge-sm">
                        Regenerating
                      </span>
                    )}
                    {segmentId && hasAudio && (
                      <div className="flex items-center gap-2">
                        {segmentUrl ? (
                          <AudioPlayer src={segmentUrl} autoPlay />
                        ) : (
                          <button
                            onClick={() => loadSegmentUrl(segmentId)}
                            disabled={isLoadingUrl}
                            className="btn btn-success btn-outline btn-sm"
                            title="Load and play audio"
                          >
                            {isLoadingUrl ? (
                              <LoaderCircle
                                size={16}
                                className="animate-spin"
                              />
                            ) : (
                              <CirclePlay size={16} />
                            )}
                          </button>
                        )}
                        <button
                          className="btn btn-sm btn-outline"
                          title="Regenerate segment"
                          onClick={() => handleRegenerate(segmentId)}
                          disabled={isRegenerating}
                        >
                          {isRegenerating ? (
                            <LoaderCircle size={16} className="animate-spin" />
                          ) : (
                            <RotateCw size={16} />
                          )}
                        </button>
                      </div>
                    )}
                    {segmentId && !hasAudio && (
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => handleRegenerate(segmentId)}
                        disabled={isRegenerating}
                      >
                        {isRegenerating ? (
                          <LoaderCircle size={16} className="animate-spin" />
                        ) : (
                          "Narrate"
                        )}
                      </button>
                    )}
                  </div>
                </div>
                <div className="flex-1">
                  <textarea
                    value={scriptSegment.text}
                    onChange={(e) => handleTextChange(index, e.target.value)}
                    className="textarea textarea-bordered w-full min-h-[80px]"
                    rows={3}
                    placeholder="Enter script text..."
                    disabled={isRegenerating}
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
