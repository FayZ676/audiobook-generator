import React from "react";
import { FileText, Edit3 } from "lucide-react";

import { Voice } from "../actions/voices";

interface ScriptControlsProps {
  isEditing: boolean;
  onToggleEditing: (editing: boolean) => void;
  voices: Voice[];
}

export default function ScriptControls({
  isEditing,
  onToggleEditing,
  voices,
}: ScriptControlsProps) {
  return (
    <div className="flex justify-between items-center">
      <h3 className="font-bold">Script controls</h3>
      <ul className="menu menu-horizontal bg-base-200 rounded-box">
        <li>
          <a
            className={!isEditing ? "active" : ""}
            onClick={() => onToggleEditing(false)}
            title="View script"
          >
            <FileText className="h-5 w-5" />
          </a>
        </li>
        <li>
          <a
            className={isEditing ? "active" : ""}
            onClick={() => onToggleEditing(true)}
            title="Edit script"
            style={
              voices.length === 0 ? { pointerEvents: "none", opacity: 0.5 } : {}
            }
          >
            <Edit3 className="h-5 w-5" />
          </a>
        </li>
      </ul>
    </div>
  );
}
