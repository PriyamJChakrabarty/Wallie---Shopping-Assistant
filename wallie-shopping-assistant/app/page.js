import { Button } from "@/components/ui/button";
import { ClerkProvider } from "@clerk/nextjs";
import Image from "next/image";

export default function Home() {
  return (
    <ClerkProvider>
      <div>
        <h2>I am back </h2>
        <Button>Click me</Button>
      </div>
    </ClerkProvider>
  );
}
