"use client";

import React from "react";

import VoiceAddForm from "./VoiceAddForm";

interface VoiceAddModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function VoiceAddModal({
  isOpen,
  onClose,
}: VoiceAddModalProps) {
  const handleClose = () => {
    onClose();
  };

  const handleSuccess = () => {
    onClose();
  };

  return (
    <div className={`modal ${isOpen ? "modal-open" : ""}`}>
      <div className="modal-box max-w-2xl">
        <h3 className="font-bold text-lg mb-4">Clone a new voice</h3>
        <VoiceAddForm onSuccess={handleSuccess} />
        <div className="modal-action">
          <button onClick={handleClose} className="btn btn-ghost">
            Cancel
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={handleClose}></div>
    </div>
  );
}