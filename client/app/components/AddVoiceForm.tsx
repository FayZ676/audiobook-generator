"use client";

import React from "react";
import { useState } from "react";

import { addVoice } from "../actions/voices";
import { handleRevalidateTag } from "../actions/revalidate";

export default function AddVoiceForm() {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [audioTranscript, setAudioTranscript] = useState("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAudioFile(e.target.files[0]);
    }
  };

  async function handleAddVoice() {
    if (name && age && gender && audioTranscript && audioFile) {
      setIsSubmitting(true);
      try {
        await addVoice({
          name,
          age,
          gender,
          audio_transcript: audioTranscript,
          audio_file: audioFile,
        });
        // Clear form
        setName("");
        setAge("");
        setGender("");
        setAudioTranscript("");
        setAudioFile(null);
        // Reset file input
        const fileInput = document.getElementById("audio-file-input") as HTMLInputElement;
        if (fileInput) {
          fileInput.value = "";
        }
        // Revalidate voices cache
        await handleRevalidateTag("voices");
      } catch (error) {
        console.error("Failed to add voice:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  const isFormValid = name && age && gender && audioTranscript && audioFile;

  return (
    <div className="flex flex-col gap-4 max-w-sm border p-4 rounded">
      <h2 className="text-lg font-semibold">Add New Voice</h2>
      
      <label htmlFor="name-input">Voice Name</label>
      <input
        id="name-input"
        name="name"
        type="text"
        className="border p-2 rounded"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter voice name"
      />

      <label htmlFor="age-input">Age</label>
      <input
        id="age-input"
        name="age"
        type="text"
        className="border p-2 rounded"
        value={age}
        onChange={(e) => setAge(e.target.value)}
        placeholder="Enter age"
      />

      <label htmlFor="gender-input">Gender</label>
      <input
        id="gender-input"
        name="gender"
        type="text"
        className="border p-2 rounded"
        value={gender}
        onChange={(e) => setGender(e.target.value)}
        placeholder="Enter gender"
      />

      <label htmlFor="transcript-input">Audio Transcript</label>
      <textarea
        id="transcript-input"
        name="audio_transcript"
        className="border p-2 rounded"
        value={audioTranscript}
        onChange={(e) => setAudioTranscript(e.target.value)}
        placeholder="Enter the transcript of the audio file"
        rows={3}
      />

      <label htmlFor="audio-file-input">Audio File</label>
      <input
        id="audio-file-input"
        name="audio_file"
        type="file"
        accept="audio/*"
        onChange={handleFileChange}
        className="border p-2 rounded"
      />

      <button
        disabled={!isFormValid || isSubmitting}
        onClick={async () => {
          await handleAddVoice();
        }}
        className="bg-blue-500 text-white p-2 rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {isSubmitting ? "Adding Voice..." : "Add Voice"}
      </button>
    </div>
  );
}