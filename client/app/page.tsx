import { createScript, getScript } from "@/app/actions/script";
import { createNarration, getNarration } from "./actions/narrate";

import Main from "@/app/components/Main";

export default async function Home() {
  const script = await getScript();
  const narrationUrl = await getNarration();

  return (
    <Main
      script={script}
      narrationUrl={narrationUrl}
      createScript={createScript}
      createNarration={createNarration}
    />
  );
}
