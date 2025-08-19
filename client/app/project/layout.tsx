import { Protect } from "@clerk/nextjs";

import Subscribe from "./subscribe";

export default function ProjectLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <Protect plan={"creator"} fallback={<Subscribe />}>
      <div className="max-w-4xl mx-auto p-4">{children}</div>
    </Protect>
  );
}
