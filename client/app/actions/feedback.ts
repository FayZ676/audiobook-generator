"use server";

import { getUserId } from "./user";

interface FeedbackData {
  message: string;
  user_id: string;
}

async function parseFeedbackFormData(formData: FormData): Promise<FeedbackData> {
  const userId = await getUserId();
  
  const message = formData.get("message") as string;
  if (!message || message.trim() === "") {
    throw new Error("Feedback message is required");
  }

  return {
    message: message.trim(),
    user_id: userId,
  };
}

export async function submitFeedback(formData: FormData) {
  const feedbackData = await parseFeedbackFormData(formData);

  try {
    const response = await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(feedbackData),
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