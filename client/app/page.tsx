import { createScript } from "@/app/actions/script";
import { getJobState } from "@/app/actions/job";

import Main from "@/app/components/Main";

export default async function Home() {
  const jobState = await getJobState();

  return <Main jobState={jobState} />;
}
