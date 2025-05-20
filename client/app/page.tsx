import { getScript } from "@/app/actions/script";

import { getNarration } from "./actions/narrate";
import { createProject } from "./actions/audiobook";
import { getJobState } from "./actions/job";

import Main from "@/app/components/Main";

export default async function Home() {
  const script = await getScript();
  const narrationUrl = await getNarration();
  const jobState = await getJobState();

  return (
    <Main
      script={script}
      narrationUrl={narrationUrl}
      jobState={jobState}
      createProject={createProject}
    />
  );
}
