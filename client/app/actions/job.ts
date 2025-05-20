import { z } from "zod";

import { auth } from "@clerk/nextjs/server";

const AudiobookJobSchema = z.object({
  job_id: z.string(),
  status: z.string(),
});

export type AudiobookJob = z.infer<typeof AudiobookJobSchema>;

export async function getJobState(): Promise<AudiobookJob | null> {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  try {
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/job/${userId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    const data = await response.json();
    const jobState = data ? AudiobookJobSchema.parse(data) : null;
    return jobState;
  } catch (error) {
    console.error("Error fetching job state:", error);
    throw error;
  }
}
