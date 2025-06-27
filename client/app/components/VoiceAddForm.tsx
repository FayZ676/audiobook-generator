"use client";

import React from "react";
import { useState } from "react";

import { AgeEnum, GenderEnum } from "../types";

import { addVoice, type Age, type Gender } from "../actions/voices";
import Tip from "./Tip";
import AudioRecorder from "./AudioRecorder";

export default function VoiceAddForm() {
  const [name, setName] = useState("");
  const [age, setAge] = useState<Age | "">("");
  const [gender, setGender] = useState<Gender | "">("");
  const [audioTranscript, setAudioTranscript] = useState("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [audioInputMode, setAudioInputMode] = useState<"upload" | "record">(
    "upload"
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAudioFile(e.target.files[0]);
    }
  };

  const handleRecordingComplete = (recordedFile: File) => {
    setAudioFile(recordedFile);
  };

  const handleAudioInputModeChange = (mode: "upload" | "record") => {
    setAudioInputMode(mode);
    setAudioFile(null); // Clear current audio file when switching modes

    // Clear file input if switching from upload mode
    if (mode === "record") {
      const fileInput = document.getElementById(
        "audio-file-input"
      ) as HTMLInputElement;
      if (fileInput) {
        fileInput.value = "";
      }
    }
  };

  async function handleAddVoice() {
    if (name && age && gender && audioTranscript && audioFile) {
      setIsSubmitting(true);
      try {
        await addVoice({
          name,
          age: age as Age,
          gender: gender as Gender,
          audio_transcript: audioTranscript,
          audio_file: audioFile,
        });

        setName("");
        setAge("");
        setGender("");
        setAudioTranscript("");
        setAudioFile(null);

        const fileInput = document.getElementById(
          "audio-file-input"
        ) as HTMLInputElement;
        if (fileInput) {
          fileInput.value = "";
        }

        // Reset audio input mode to upload
        setAudioInputMode("upload");
      } catch (error) {
        console.error("Failed to add voice:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  const isFormValid = name && age && gender && audioTranscript && audioFile;

  return (
    <div className="flex flex-col gap-2 bg-base-200 p-4 rounded">
      <label htmlFor="name-input" className="font-medium">
        Name
      </label>
      <input
        id="name-input"
        name="name"
        type="text"
        className="bg-base-300 p-2 rounded"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter voice name"
        required
      />

      <div className="grid grid-cols-2 gap-2">
        <div className="flex flex-col gap-2">
          <label htmlFor="age-select" className="font-medium">
            Age
          </label>
          <select
            id="age-select"
            name="age"
            className="bg-base-300 p-2 rounded"
            value={age}
            onChange={(e) => setAge(e.target.value as Age)}
            required
          >
            <option value="">Select age</option>
            {AgeEnum.options.map((ageValue) => (
              <option key={ageValue} value={ageValue}>
                {ageValue.charAt(0).toUpperCase() + ageValue.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-2">
          <label htmlFor="gender-select" className="font-medium">
            Gender
          </label>
          <select
            id="gender-select"
            name="gender"
            className="bg-base-300 p-2 rounded"
            value={gender}
            onChange={(e) => setGender(e.target.value as Gender)}
            required
          >
            <option value="">Select gender</option>
            {GenderEnum.options.map((genderValue) => (
              <option key={genderValue} value={genderValue}>
                {genderValue.charAt(0).toUpperCase() + genderValue.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <label htmlFor="audio-input-mode" className="font-medium">
        Audio Sample
      </label>
      <Tip variant="info">Keep your audio file under 12 seconds.</Tip>
      <div className="grid grid-cols-2 gap-2">
        <button
          type="button"
          onClick={() => handleAudioInputModeChange("upload")}
          className={`btn btn-sm ${
            audioInputMode === "upload" ? "btn-primary" : "btn-outline"
          }`}
        >
          Upload
        </button>
        <button
          type="button"
          onClick={() => handleAudioInputModeChange("record")}
          className={`btn btn-sm ${
            audioInputMode === "record" ? "btn-primary" : "btn-outline"
          }`}
        >
          Record
        </button>
      </div>

      {audioInputMode === "upload" ? (
        <>
          <label htmlFor="audio-file-input" className="font-medium">
            Audio File
          </label>
          <input
            id="audio-file-input"
            name="audio_file"
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            className="bg-base-300 p-2 rounded"
            required
          />
          {audioFile && audioInputMode === "upload" && (
            <div className="text-sm text-success">
              ✓ File selected: {audioFile.name}
            </div>
          )}
        </>
      ) : (
        <>
          <label className="font-medium">Record Audio Sample</label>
          <AudioRecorder
            onRecordingComplete={handleRecordingComplete}
            maxDuration={12}
          />
          {audioFile && audioInputMode === "record" && (
            <div className="text-sm text-success">
              ✓ Recording complete: {audioFile.name}
            </div>
          )}
        </>
      )}

      <label htmlFor="transcript-input" className="font-medium">
        Audio Transcript
      </label>
      <textarea
        id="transcript-input"
        name="audio_transcript"
        className="bg-base-300 p-2 rounded"
        value={audioTranscript}
        onChange={(e) => setAudioTranscript(e.target.value)}
        placeholder="Enter the transcript of the audio file"
        rows={3}
        required
      />

      <button
        disabled={!isFormValid || isSubmitting}
        onClick={async () => {
          await handleAddVoice();
        }}
        className="btn btn-block"
      >
        {isSubmitting ? "Adding Voice..." : "Add Voice"}
      </button>
    </div>
  );
}
