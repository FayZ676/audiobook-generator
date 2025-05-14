import { createScript, getScript, deleteScript } from "@/app/actions/script";
import { uploadTextFile } from "@/app/actions/file";

import Main from "@/app/components/Main";

export default async function Home() {
  const script = await getScript();
  // Get narrations as well.

  return (
    <Main
      script={script}
      uploadTextFile={uploadTextFile}
      createScript={createScript}
      deleteScript={deleteScript}
    />
  );
}
