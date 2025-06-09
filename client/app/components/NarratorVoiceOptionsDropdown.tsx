"use client";

import React from "react";
import { use } from "react";

import { Voice } from "../actions/voices";

interface NarratorVoiceOptionsDropdownProps {
  voicesPromise: Promise<Voice[]>;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function NarratorVoiceOptionsDropdown({
  voicesPromise,
  value,
  onChange,
  disabled = false,
}: NarratorVoiceOptionsDropdownProps) {
  const voices = use(voicesPromise);

  return (
    <select
      id="narrator-input"
      name="narrator"
      className="bg-gray-200 p-2 rounded"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
    >
      <option value="">Select a narrator voice</option>
      {voices.map((voice) => (
        <option key={voice.name} value={voice.name}>
          {voice.name}
        </option>
      ))}
    </select>
  );
}