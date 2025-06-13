import React from "react";

interface TipProps {
  children: React.ReactNode;
  variant?: "info" | "warning" | "success";
  className?: string;
}

export default function Tip({
  children,
  variant = "info",
  className = "",
}: TipProps) {
  const baseClasses =
    "text-sm p-3 rounded-lg bg-opacity-50 flex items-start gap-2";

  const variantClasses = {
    info: "bg-blue-50 border-blue-400 text-blue-800",
    warning: "bg-yellow-50 border-yellow-400 text-yellow-800",
    success: "bg-green-50 border-green-400 text-green-800",
  };

  const iconClasses = {
    info: "text-blue-500",
    warning: "text-yellow-500",
    success: "text-green-500",
  };

  const combinedClasses =
    `${baseClasses} ${variantClasses[variant]} ${className}`.trim();

  // Simple icon using Unicode characters for minimal dependency
  const getIcon = () => {
    switch (variant) {
      case "info":
        return "💡";
      case "warning":
        return "⚠️";
      case "success":
        return "✅";
      default:
        return "ℹ️";
    }
  };

  return (
    <div role="alert" className="alert">
      <span>{getIcon()}</span>
      <span>{children}</span>
    </div>
  );
}
