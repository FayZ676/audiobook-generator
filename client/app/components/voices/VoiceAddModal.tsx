"use client";

import React from "react";
import { useState, useRef } from "react";

import { AgeEnum, GenderEnum } from "../../types";

import { addVoice, type Age, type Gender } from "../../actions/voices";
import Tip from "../ui/Tip";
import AudioRecorder from "../audio/AudioRecorder";

import { Mic, Upload, Check } from "lucide-react";

interface VoiceAddModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function VoiceAddModal({ isOpen, onClose }: VoiceAddModalProps) {
  const [name, setName] = useState("");
  const [age, setAge] = useState<Age | "">("");
  const [gender, setGender] = useState<Gender | "">("");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [audioInputMode, setAudioInputMode] = useState<"upload" | "record">(
    "upload"
  );
  const modalRef = useRef<HTMLDialogElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAudioFile(e.target.files[0]);
    }
  };

  const handleAudioInputModeChange = (mode: "upload" | "record") => {
    setAudioInputMode(mode);
    setAudioFile(null);

    if (mode === "upload") {
      const fileInput = document.getElementById(
        "audio-file-input"
      ) as HTMLInputElement;
      if (fileInput) {
        fileInput.value = "";
        fileInput.click();
      }
    } else if (mode === "record") {
      modalRef.current?.showModal();
    }
  };

  const handleModalRecordingComplete = (recordedFile: File) => {
    setAudioFile(recordedFile);
  };

  async function handleAddVoice() {
    if (name && age && gender && audioFile) {
      setIsSubmitting(true);
      try {
        await addVoice({
          name,
          age: age as Age,
          gender: gender as Gender,
          audio_file: audioFile,
        });

        setName("");
        setAge("");
        setGender("");
        setAudioFile(null);

        const fileInput = document.getElementById(
          "audio-file-input"
        ) as HTMLInputElement;
        if (fileInput) {
          fileInput.value = "";
        }

        setAudioInputMode("upload");

        onClose();
      } catch (error) {
        console.error("Failed to add voice:", error);
      } finally {
        setIsSubmitting(false);
      }
    }
  }

  const handleClose = () => {
    onClose();
  };

  const isFormValid = name && age && gender && audioFile;

  return (
    <div className={`modal ${isOpen ? "modal-open" : ""}`}>
      <div className="modal-box max-w-2xl">
        <div className="flex flex-col gap-2 rounded">
          <div className="prose prose-base max-w-none">
            <label htmlFor="name-input">Name</label>
          </div>
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
              <div className="prose prose-base max-w-none">
                <label htmlFor="age-select">Age</label>
              </div>
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
              <div className="prose prose-base max-w-none">
                <label htmlFor="gender-select">Gender</label>
              </div>
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

          <div className="prose prose-base max-w-none">
            <label htmlFor="audio-input-mode">Audio Sample</label>
          </div>
          <Tip variant="info">Keep your audio file under 12 seconds.</Tip>

          <input
            id="audio-file-input"
            name="audio_file"
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            className="hidden"
            required
          />

          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleAudioInputModeChange("upload")}
              className="btn"
            >
              <Upload className="h-4 w-4 mr-2" />
            </button>
            <button
              type="button"
              onClick={() => handleAudioInputModeChange("record")}
              className="btn"
            >
              <Mic className="h-4 w-4 mr-2" />
            </button>
          </div>

          {audioFile && (
            <div className="flex gap-1 items-center text-sm text-success">
              <Check size={16} /> Audio recording ready
            </div>
          )}
        </div>
        <div className="modal-action">
          <button
            disabled={!isFormValid || isSubmitting}
            onClick={async () => {
              await handleAddVoice();
            }}
            className="btn"
          >
            {isSubmitting ? "Adding Voice" : "Add Voice"}
          </button>
          <button onClick={handleClose} className="btn btn-ghost">
            Cancel
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={handleClose}></div>

      <dialog id="audio-modal" className="modal" ref={modalRef}>
        <div className="modal-box">
          {audioInputMode === "upload" ? (
            <div className="flex flex-col gap-4">
              <Tip variant="info">Select an audio file under 12 seconds.</Tip>
              <input
                id="modal-audio-file-input"
                name="audio_file"
                type="file"
                accept="audio/*"
                onChange={handleFileChange}
                className="file-input file-input-bordered w-full"
                required
              />
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              <AudioRecorder
                onRecordingComplete={handleModalRecordingComplete}
                maxDuration={12}
              />
            </div>
          )}
        </div>
        <form method="dialog" className="modal-backdrop">
          <button>close</button>
        </form>
      </dialog>
    </div>
  );
}
