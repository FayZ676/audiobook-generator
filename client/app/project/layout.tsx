import { Protect } from "@clerk/nextjs";

export default function ProjectLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <Protect
      plan={"creator"}
      fallback={
        <div className="text-center">Subscribe to access this content.</div>
      }
    >
      {children}
    </Protect>
  );
}
