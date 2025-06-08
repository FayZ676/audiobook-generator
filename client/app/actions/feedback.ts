"use server";

import { getUserId } from "./user";

export async function submitFeedback(formData: FormData) {
  const userId = await getUserId();

  const message = formData.get("message") as string;
  if (!message || message.trim() === "") {
    throw new Error("Feedback message is required");
  }

  try {
    const response = await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message.trim(),
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit feedback: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error submitting feedback:", error);
    throw error;
  }
}