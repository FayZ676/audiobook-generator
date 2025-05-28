import { getScript } from "@/app/actions/script";

import { hasNarration } from "@/app/actions/narrate";
import { createScript } from "@/app/actions/script";
import { createNarration } from "@/app/actions/narrate";
import { getJobState } from "@/app/actions/job";
import { auth } from "@clerk/nextjs/server";

import Main from "@/app/components/Main";

export default async function Home() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }
  
  const script = await getScript();
  const narrationExists = await hasNarration();
  const jobState = await getJobState();

  return (
    <Main
      createScript={createScript}
      createNarration={createNarration}
      script={script}
      hasNarration={narrationExists}
      userId={userId}
      jobState={jobState}
    />
  );
}
