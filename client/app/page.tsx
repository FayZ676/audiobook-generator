import { getScript } from "@/app/actions/script";

import { getNarration } from "@/app/actions/narrate";
import { createScript } from "@/app/actions/script";
import { createNarration } from "@/app/actions/narrate";
import { getJobState } from "@/app/actions/job";

import Main from "@/app/components/Main";

export default async function Home() {
  const narrationUrl = await getNarration();
  const jobState = await getJobState();

  return (
    <Main
      createScript={createScript}
      createNarration={createNarration}
      narrationUrl={narrationUrl}
      jobState={jobState}
    />
  );
}
