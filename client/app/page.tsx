import { getScript } from "@/app/actions/script";

import { createScript } from "@/app/actions/script";
import { createNarration } from "@/app/actions/narrate";
import { getJobState } from "@/app/actions/job";

import Main from "@/app/components/Main";

export default async function Home() {
  const script = await getScript();
  const jobState = await getJobState();

  return (
    <Main
      createScript={createScript}
      createNarration={createNarration}
      script={script}
      jobState={jobState}
    />
  );
}
