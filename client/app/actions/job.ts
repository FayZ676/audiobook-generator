import { z } from "zod";

import { auth } from "@clerk/nextjs/server";

const AudiobookJobSchema = z.object({
  job_id: z.string(),
  script_status: z.enum(["processing", "failed"]).nullable(),
  narration_status: z.enum(["processing", "failed"]).nullable(),
});

export type AudiobookJob = z.infer<typeof AudiobookJobSchema>;

export async function getJobState(): Promise<AudiobookJob | null> {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  try {
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/job/status/${userId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        cache: "force-cache",
      }
    );
    if (!response.ok) {
      throw new Error(
        `Error retrieving job status: ${response.status} ${response.statusText}`
      );
    }
    const data = await response.json();
    const jobState = data ? AudiobookJobSchema.parse(data) : null;
    return jobState;
  } catch (error) {
    console.error("Error fetching job state:", error);
    throw error;
  }
}
