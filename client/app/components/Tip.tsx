import React from "react";

interface TipProps {
  children: React.ReactNode;
  variant?: "info" | "warning" | "success";
  className?: string;
}

export default function Tip({ children, variant = "info" }: TipProps) {
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
