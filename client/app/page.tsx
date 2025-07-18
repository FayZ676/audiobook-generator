import Link from "next/link";

import { Waitlist } from "@clerk/nextjs";

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <div className="hero min-h-[70vh]">
        <div className="hero-content text-center">
          <div className="max-w-md">
            <h1 className="text-5xl font-bold">
              The Future of Audiobooks is Here
            </h1>
            <p className="py-6">
              Turn your text into engaging multi-speaker audiobooks within
              minutes.
            </p>
            <div className="flex flex-col gap-4">
              <Link href="#demo" className="btn btn-primary">
                See Demo
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Waitlist Section */}
      <div className="py-16 px-4">
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-4">Join the Waitlist</h2>
          <div className="flex justify-center">
            <Waitlist />
          </div>
        </div>
      </div>
    </div>
  );
}
