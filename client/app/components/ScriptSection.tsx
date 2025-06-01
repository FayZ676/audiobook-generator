import React from "react";

import { Script } from "../actions/script";
import ScriptTextClient from "@/app/components/ScriptTextClient";
import GenerateScriptForm from "./GenerateScriptForm";

interface ScriptSectionProps {
  scriptPromise: Promise<Script | null>;
}

export default async function ScriptSection({
  scriptPromise,
}: ScriptSectionProps) {
  const script = await scriptPromise;
  return script ? <ScriptTextClient script={script} /> : <GenerateScriptForm />;
}
