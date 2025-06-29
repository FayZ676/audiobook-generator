import React, { useState } from "react";
import { Age, Gender } from "@/app/actions/voices";
import { ManualCharacter } from "@/app/types";
import { AgeEnum, GenderEnum } from "@/app/types";

interface AddCharacterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddCharacter: (character: ManualCharacter) => void;
}

export default function AddCharacterModal({
  isOpen,
  onClose,
  onAddCharacter,
}: AddCharacterModalProps) {
  const [newCharacterName, setNewCharacterName] = useState("");
  const [newCharacterAge, setNewCharacterAge] = useState<Age | "">("");
  const [newCharacterGender, setNewCharacterGender] = useState<Gender | "">("");

  const handleAddCharacter = () => {
    if (newCharacterName.trim() && newCharacterAge && newCharacterGender) {
      const character: ManualCharacter = {
        name: newCharacterName.trim(),
        age: newCharacterAge,
        gender: newCharacterGender,
      };
      onAddCharacter(character);
      setNewCharacterName("");
      setNewCharacterAge("");
      setNewCharacterGender("");
      onClose();
    }
  };

  const handleClose = () => {
    setNewCharacterName("");
    setNewCharacterAge("");
    setNewCharacterGender("");
    onClose();
  };

  const isFormValid =
    newCharacterName.trim() && newCharacterAge && newCharacterGender;

  return (
    <div className={`modal ${isOpen ? "modal-open" : ""}`}>
      <div className="modal-box">
        <div className="space-y-4">
          <div>
            <label className="label">
              <span className="label-text">Character Name</span>
            </label>
            <input
              type="text"
              placeholder="Enter character name"
              value={newCharacterName}
              onChange={(e) => setNewCharacterName(e.target.value)}
              className="input input-bordered w-full"
            />
          </div>

          <div>
            <label className="label">
              <span className="label-text">Age</span>
            </label>
            <select
              value={newCharacterAge}
              onChange={(e) => setNewCharacterAge(e.target.value as Age)}
              className="select select-bordered w-full"
            >
              <option value="">Select age</option>
              {AgeEnum.options.map((age) => (
                <option key={age} value={age}>
                  {age}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">
              <span className="label-text">Gender</span>
            </label>
            <select
              value={newCharacterGender}
              onChange={(e) => setNewCharacterGender(e.target.value as Gender)}
              className="select select-bordered w-full"
            >
              <option value="">Select gender</option>
              {GenderEnum.options.map((gender) => (
                <option key={gender} value={gender}>
                  {gender}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="modal-action">
          <button onClick={handleClose} className="btn btn-ghost">
            Cancel
          </button>
          <button
            onClick={handleAddCharacter}
            disabled={!isFormValid}
            className="btn btn-primary"
          >
            Add Character
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={handleClose}></div>
    </div>
  );
}
