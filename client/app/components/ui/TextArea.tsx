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
    <div
      contentEditable={!disabled}
      role="textbox"
      aria-placeholder={placeholder}
      className={`textarea w-full overflow-y-auto outline-none ${className}`}
      style={{
        minHeight,
        maxHeight,
        opacity: disabled ? 0.6 : 1,
        cursor: disabled ? "not-allowed" : "text",
      }}
      suppressContentEditableWarning={true}
      onInput={(e) => {
        const target = e.target as HTMLDivElement;
        onChange(target.textContent || "");
      }}
      onBlur={onBlur}
      dangerouslySetInnerHTML={{
        __html: value || `<span class="text-gray-400">${placeholder}</span>`,
      }}
    />
  );
}
