"use server";

interface WaitlistData {
  email: string;
}

async function parseWaitlistFormData(formData: FormData): Promise<WaitlistData> {
  const email = formData.get("email") as string;
  if (!email || email.trim() === "") {
    throw new Error("Email is required");
  }

  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.trim())) {
    throw new Error("Please enter a valid email address");
  }

  return {
    email: email.trim().toLowerCase(),
  };
}

export async function submitWaitlist(formData: FormData) {
  const waitlistData = await parseWaitlistFormData(formData);

  try {
    // For now, just log the email (in a real app, this would save to database or service)
    console.log("Waitlist signup:", waitlistData.email);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    return { success: true, message: "Successfully joined the waitlist!" };
  } catch (error) {
    console.error("Error submitting waitlist:", error);
    throw error;
  }
}