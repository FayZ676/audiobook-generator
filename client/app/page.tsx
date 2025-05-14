import { createScript, getScript, deleteScript } from "@/app/actions/script";

import Main from "@/app/components/Main";

export default async function Home() {
  const script = await getScript();
  // Get narrations as well.

  return <Main script={script} createScript={createScript} />;
}
