"use client"
import { SignUp } from '@clerk/nextjs'
import React from 'react'

function Page() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
        <SignUp/>
    </div>
  )
}

export default Page