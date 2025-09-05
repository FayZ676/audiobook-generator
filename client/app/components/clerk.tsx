"use client";

import { useUser } from "@clerk/nextjs";
import { ReactNode } from "react";

interface ClerkWrapperProps {
  children: (userId: string) => ReactNode;
}

export default function ClerkWrapper({ children }: ClerkWrapperProps) {
  const { isSignedIn, user, isLoaded } = useUser();

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  if (!isSignedIn) {
    // TODO: Redirect to signin
    return <div>Sign In</div>;
  }

  return <>{children(user.id)}</>;
}
