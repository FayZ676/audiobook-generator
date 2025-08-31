"use client";

import React from "react";

interface TextAreaProps {
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  minHeight?: string;
  maxHeight?: string;
}

export default function TextArea({
  value,
  onChange,
  onBlur,
  placeholder = "Enter text...",
  disabled = false,
  className = "",
  minHeight = "2rem",
  maxHeight = "12rem",
}: TextAreaProps) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      onBlur={onBlur}
      placeholder={placeholder}
      disabled={disabled}
      className={`textarea w-full resize-none ${className}`}
      style={{
        minHeight,
        maxHeight,
      }}
    />
  );
}
