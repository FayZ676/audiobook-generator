import Image from "next/image";

import { Waitlist } from "@clerk/nextjs";

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <div className="hero bg-base-200 min-h-[70vh]">
        <div className="hero-content flex-col lg:flex-row-reverse">
          <Image
            src="dashboard.png"
            className="min-w-[300px] rounded-lg shadow-2xl"
            alt="Dashboard Screenshot"
          />
          <div className="flex flex-col gap-8">
            <h1 className="text-5xl font-bold">
              Your Stories Brought to Life<br></br>Exactly as Imagined
            </h1>
            <p className="text-xl font-medium">
              Produce multi-voice audiobooks with complete control. Customize
              characters, clone voices instantly, edit scripts on the fly ... Or
              let the studio handle it all for you.
            </p>
          </div>
        </div>
      </div>

      {/* Demo */}

      {/* Testimonials */}
      <div></div>

      {/* Features */}
      <div className="py-16 px-4 bg-base-100">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            One Goal in Mind
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card bg-base-200 shadow-lg">
              <div className="card-body text-center">
                <h3 className="card-title justify-center text-xl mb-4">
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
              <div className="card-body text-center">
                <h3 className="card-title justify-center text-xl mb-4">
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
      <div className="py-16 px-4">
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-4">Join the Waitlist</h2>
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
