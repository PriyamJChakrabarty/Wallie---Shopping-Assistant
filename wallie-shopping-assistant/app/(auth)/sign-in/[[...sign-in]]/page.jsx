"use client";
import { SignIn } from '@clerk/nextjs';
import React from 'react';

function Page() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <SignIn />
    </div>
  );
}

export default Page;
