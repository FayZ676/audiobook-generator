import { Waitlist } from "@clerk/nextjs";

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <div className="hero bg-base-200 min-h-[70vh]">
        <div className="hero-content flex-col lg:flex-row-reverse">
          <img
            src="dashboard.png"
            className="max-w-2xl rounded-lg shadow-2xl"
          />
          <div className="flex flex-col gap-8">
            <h1 className="text-5xl font-bold">
              Your Stories<br></br>Brought to Life<br></br>Exactly as Imagined
            </h1>
            <p className="text-xl font-medium">
              Produce multi-voice audiobooks with complete control. Customize
              characters, clone voices instantly, edit scripts on the fly ... Or
              let the studio handle it all for you.
            </p>
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
