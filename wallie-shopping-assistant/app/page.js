"use client";
import { SignedIn, SignedOut, RedirectToSignIn } from "@clerk/nextjs";
import { redirect } from "next/navigation";

export default function HomePage() {
  return (
    <>
      <SignedIn>
        {/* 👇 if user is signed in, show dashboard directly */}
        {redirect("/dashboard")}
      </SignedIn>

      <SignedOut>
        {/* 👇 Clerk handles showing sign-in page */}
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
}
