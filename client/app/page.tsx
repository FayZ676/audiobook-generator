import { getScript } from "@/app/actions/script";
import { getNarration } from "./actions/narrate";
import { createProject } from "./actions/audiobook";

import Main from "@/app/components/Main";

export default async function Home() {
  const script = await getScript();
  const narrationUrl = await getNarration();
  console.log("narrationUrl", narrationUrl);
  console.log("script", script);

  return (
    <Main
      script={script}
      narrationUrl={narrationUrl}
      createProject={createProject}
    />
  );
}
