"use client";

import { useUser } from "@clerk/nextjs";
import { UserResource } from "@clerk/types";
import { ReactElement, cloneElement } from "react";

interface ClerkWrapperProps {
  children: ReactElement<{ user: UserResource }>;
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

  return cloneElement(children, { user });
}
