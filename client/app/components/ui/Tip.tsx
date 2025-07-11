import React from "react";

interface TipProps {
  children: React.ReactNode;
  variant?: "info" | "warning" | "success";
  className?: string;
}

export default function Tip({ children, variant = "info" }: TipProps) {
  const getClassName = () => {
    switch (variant) {
      case "info":
        return "alert-info";
      case "warning":
        return "alert-warning";
      case "success":
        return "alert-success";
    }
  };

  return (
    <div role="alert" className={`alert ${getClassName()} alert-soft`}>
      <span>{children}</span>
    </div>
  );
}
