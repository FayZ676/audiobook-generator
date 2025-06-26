import Link from "next/link";
import { Play, Mic, Edit, Check } from "lucide-react";
import WaitlistForm from "./components/WaitlistForm";
import DemoAudio from "./components/DemoAudio";

export default function Home() {
  return (
    <div className="flex flex-col px-4">
      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] text-center">
        <h1 className="text-4xl font-bold mb-4">Audiobook Generator</h1>
        <p className="text-lg text-gray-600 mb-8 max-w-2xl">
          Transform your text into engaging multi-speaker audiobooks with AI-powered narration.
        </p>
        <div className="flex flex-col gap-4 w-full max-w-sm">
          <Link href="/project" className="btn btn-primary btn-lg">
            Get Started
          </Link>
          <Link href="#demo" className="btn btn-outline">
            See Demo
          </Link>
        </div>
      </div>

      {/* Demo Section */}
      <div id="demo" className="py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Experience the Magic</h2>
        
        {/* Audiobook Sample Demo */}
        <div className="mb-12">
          <div className="flex items-center gap-2 mb-4">
            <Play className="h-6 w-6 text-primary" />
            <h3 className="text-xl font-semibold">Multi-Speaker Audiobook Sample</h3>
          </div>
          <div className="bg-base-200 p-6 rounded-lg">
            <p className="text-sm text-gray-600 mb-4">
              Listen to how different AI voices bring characters to life:
            </p>
            <div className="space-y-3">
              <DemoAudio
                speaker="Narrator"
                voiceType="Professional Voice"
                text="The story begins on a cold winter evening, when our protagonist discovers something extraordinary."
                colorClass="border-blue-500"
              />
              <DemoAudio
                speaker="Alice"
                voiceType="Young Female"
                text="I can't believe what I'm seeing! This changes everything we thought we knew."
                colorClass="border-green-500"
              />
              <DemoAudio
                speaker="Bob"
                voiceType="Middle-aged Male"
                text="Now hold on just a minute. We need to think this through carefully before we act."
                colorClass="border-purple-500"
              />
            </div>
          </div>
        </div>

        {/* Voice Cloning Demo */}
        <div className="mb-12">
          <div className="flex items-center gap-2 mb-4">
            <Mic className="h-6 w-6 text-primary" />
            <h3 className="text-xl font-semibold">Voice Cloning</h3>
          </div>
          <div className="bg-base-200 p-6 rounded-lg">
            <p className="text-sm text-gray-600 mb-4">
              Clone any voice with just a 12-second audio sample:
            </p>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-base-100 rounded">
                <div>
                  <div className="font-medium">Emma Watson</div>
                  <div className="text-xs text-gray-500">Young • Female</div>
                </div>
                <button className="btn btn-sm btn-outline">
                  Play Sample
                </button>
              </div>
              <div className="flex items-center justify-between p-3 bg-base-100 rounded">
                <div>
                  <div className="font-medium">Morgan Freeman</div>
                  <div className="text-xs text-gray-500">Mature • Male</div>
                </div>
                <button className="btn btn-sm btn-outline">
                  Play Sample
                </button>
              </div>
            </div>
            <div className="mt-4">
              <Link href="/voices" className="btn btn-primary btn-sm">
                Create Your Voice Clone
              </Link>
            </div>
          </div>
        </div>

        {/* Script Editing Demo */}
        <div className="mb-12">
          <div className="flex items-center gap-2 mb-4">
            <Edit className="h-6 w-6 text-primary" />
            <h3 className="text-xl font-semibold">Script Editing</h3>
          </div>
          <div className="bg-base-200 p-6 rounded-lg">
            <p className="text-sm text-gray-600 mb-4">
              Edit your script with real-time voice assignment:
            </p>
            <div className="space-y-3">
              <DemoAudio
                speaker="Narrator" 
                voiceType="Professional Voice"
                text="It was a dark and stormy night when Alice discovered the mysterious letter..."
                colorClass="border-primary"
              />
              <DemoAudio
                speaker="Alice"
                voiceType="Young Female" 
                text="What could this mean? I must find out the truth!"
                colorClass="border-green-500"
              />
            </div>
            <div className="mt-4">
              <Link href="/project" className="btn btn-primary btn-sm">
                Try Script Editor
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="py-16 bg-base-100">
        <h2 className="text-3xl font-bold text-center mb-12">Simple Pricing</h2>
        <div className="max-w-sm mx-auto">
          <div className="bg-base-200 p-6 rounded-lg border-2 border-primary">
            <div className="text-center">
              <h3 className="text-xl font-semibold mb-2">Early Access</h3>
              <div className="text-3xl font-bold text-primary mb-1">Free</div>
              <div className="text-sm text-gray-600 mb-6">During Beta</div>
              
              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Unlimited voice cloning</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Multi-speaker audiobooks</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Script editing tools</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span className="text-sm">High-quality output</span>
                </div>
              </div>
              
              <Link href="/project" className="btn btn-primary btn-block mb-4">
                Start Creating
              </Link>
              <p className="text-xs text-gray-500">
                No credit card required
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Waitlist Section */}
      <div className="py-16">
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-4">Join the Waitlist</h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Be the first to know when new features are released and get priority access to advanced capabilities.
          </p>
          
          <WaitlistForm />
        </div>
      </div>
    </div>
  );
}
