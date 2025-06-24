"use server";

import { z } from "zod";

import { auth } from "@clerk/nextjs/server";

const AudiobookJobSchema = z.object({
  job_id: z.string(),
  script_status: z.enum(["processing", "complete", "failed"]).nullable(),
  narration_status: z.enum(["processing", "complete", "failed"]).nullable(),
  message: z.string().nullable(),
  script_started_at: z.string().nullable().optional(),
  narration_started_at: z.string().nullable().optional(),
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
        next: {
          tags: ["job"],
        },
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

export async function deleteJob(filename: string): Promise<void> {
  try {
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/job/status/${filename}`,
      {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    if (!response.ok) {
      throw new Error(
        `Error deleting job: ${response.status} ${response.statusText}`
      );
    }
  } catch (error) {
    console.error("Error deleting job:", error);
    throw error;
  }
}
