import React from "react";

interface ControlButtonProps {
  children: React.ReactNode;
  onClick: (e: React.MouseEvent) => void;
  disabled?: boolean;
  variant?: "primary" | "destructive";
  className?: string;
}

export default function ControlButton({
  children,
  onClick,
  disabled = false,
  variant = "primary",
  className = "",
}: ControlButtonProps) {
  const baseClasses = "py-2 px-4 rounded font-medium transition-colors duration-200 disabled:cursor-not-allowed disabled:opacity-50";
  
  const variantClasses = {
    primary: "bg-blue-500 text-white hover:bg-blue-600 active:bg-blue-700 disabled:bg-gray-300 disabled:text-gray-500",
    destructive: "bg-red-500 text-white hover:bg-red-600 active:bg-red-700 disabled:bg-gray-300 disabled:text-gray-500",
  };

  const combinedClasses = `${baseClasses} ${variantClasses[variant]} ${className}`.trim();

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={combinedClasses}
    >
      {children}
    </button>
  );
}