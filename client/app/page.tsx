import { createScript, getScript, deleteScript } from "@/app/actions/script";
import { createNarration, getNarration } from "./actions/narrate";

import Main from "@/app/components/Main";

export default async function Home() {
  const script = await getScript();
  const narration = await getNarration();
  // Get narrations as well.

  return (
    <Main
      script={script}
      narration={narration}
      createScript={createScript}
      createNarration={createNarration}
    />
  );
}
