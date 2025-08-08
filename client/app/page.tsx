import Image from "next/image";

import { Waitlist } from "@clerk/nextjs";

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <div className="hero bg-base-200 min-h-[50vh]">
        <div className="hero-content flex-col md:flex-row-reverse md:gap-16">
          <Image
            src="/dashboard.png"
            height={1500}
            width={1500}
            className="min-w-[300px] rounded-lg shadow-2xl"
            alt="Dashboard Screenshot"
          />
          <div className="flex flex-col">
            <h1 className="leading-snug">
              Your Stories<br></br>Brought to Life<br></br>Exactly as Imagined
            </h1>
            <p>
              Produce multi-voice audiobooks with complete control. Customize
              characters, clone voices instantly, edit scripts on the fly, or
              let the studio handle it all for you.
            </p>
          </div>
        </div>
      </div>

      {/* Demo */}

      {/* Testimonials */}
      <div></div>

      {/* Features */}
      <div className="bg-base-100">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-center">One Goal in Mind</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card bg-base-200 shadow-lg">
              <div className="card-body">
                <h3 className="card-title justify-center">
                  Multi Speaker Narration
                </h3>
                <p>
                  Clone any voice instantly with just a few seconds of audio.
                  Create unique character voices that bring your stories to
                  life.
                </p>
              </div>
            </div>
            <div className="card bg-base-200 shadow-lg">
              <div className="card-body">
                <h3 className="card-title justify-center">
                  Instant Voice Cloning
                </h3>
                <p>
                  Let our AI studio handle the entire production process
                  automatically, from character assignment to final audio
                  mastering.
                </p>
              </div>
            </div>
            <div className="card bg-base-200 shadow-lg">
              <div className="card-body text-center">
                <h3 className="card-title justify-center text-xl mb-4">
                  Edit Everything
                </h3>
                <p>
                  Edit and refine your scripts with our intuitive editor. Make
                  real-time adjustments to dialogue, pacing, and character
                  interactions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Waitlist */}
      <div className="">
        <div className="text-center">
          <h2 className="">Join the Waitlist</h2>
          <div className="flex justify-center">
            <Waitlist />
          </div>
        </div>
      </div>

      {/* About Me */}
      <div></div>
    </div>
  );
}
