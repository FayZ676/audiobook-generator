"use client";

import React, { useState } from "react";
import { submitWaitlist } from "../actions/waitlist";

export default function WaitlistForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (formData: FormData) => {
    setIsSubmitting(true);
    setMessage("");

    try {
      await submitWaitlist(formData);
      setIsSuccess(true);
      setMessage("Thank you! You've been added to the waitlist.");
      
      // Reset form
      const form = document.getElementById("waitlist-form") as HTMLFormElement;
      if (form) {
        form.reset();
      }
    } catch (error) {
      setIsSuccess(false);
      setMessage(error instanceof Error ? error.message : "Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto">
      <form id="waitlist-form" action={handleSubmit} className="space-y-4">
        <input
          type="email"
          name="email"
          placeholder="Enter your email"
          className="input input-bordered w-full"
          required
          disabled={isSubmitting}
        />
        <button 
          type="submit" 
          className="btn btn-primary btn-block"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Joining..." : "Join Waitlist"}
        </button>
      </form>
      
      {message && (
        <div className={`mt-4 p-3 rounded ${isSuccess ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          <p className="text-sm text-center">{message}</p>
        </div>
      )}
      
      <p className="text-xs text-gray-500 mt-4 text-center">
        We respect your privacy. No spam, ever.
      </p>
    </div>
  );
}