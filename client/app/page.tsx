import { createScript, getScripts, deleteScript } from "@/app/actions/script";
import { uploadTextFile } from "@/app/actions/file";

import Main from "@/app/components/Main";

export default async function Home() {
  const scripts = await getScripts();
  // Get narrations as well.

  return (
    <Main
      scripts={scripts}
      uploadTextFile={uploadTextFile}
      createScript={createScript}
      deleteScript={deleteScript}
    />
  );
}
