"use server";

import { unstable_cache } from "next/cache";
import { getCurrentProjectName } from "./project";
import { getChapters } from "./chapter";
import { getJobState, AudiobookJob } from "./job";
import { getVoices, Voice } from "./voices";
import { getScript, Script } from "./script";
import { getNarration, NarrationUrl } from "./narrate";
import { getUserId } from "./user";

export interface DashboardData {
  projectName: string;
  chapters: string[];
  jobState: AudiobookJob | null;
  voices: Voice[];
  script?: Script | null;
  narration?: NarrationUrl | null;
}

async function getDashboardDataInternal(
  selectedChapter?: string
): Promise<DashboardData> {
  const [projectName, chapters, jobState, voices] = await Promise.all([
    getCurrentProjectName(),
    getChapters(),
    getJobState(),
    getVoices(),
  ]);

  let script: Script | null = null;
  let narration: NarrationUrl | null = null;

  if (selectedChapter) {
    [script, narration] = await Promise.all([
      getScript(selectedChapter),
      getNarration(selectedChapter),
    ]);
  }

  return {
    projectName,
    chapters,
    jobState,
    voices,
    script,
    narration,
  };
}

export const getDashboardData = async (selectedChapter?: string) => {
  const userId = await getUserId();
  return unstable_cache(
    getDashboardDataInternal,
    [`dashboard-data-${userId}-${selectedChapter || 'root'}`],
    {
      tags: ["project", "chapters", "job", "voices", "script", "narration"],
      revalidate: 60,
    }
  )(selectedChapter);
};