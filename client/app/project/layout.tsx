import { Protect } from "@clerk/nextjs";

import Subscribe from "./subscribe";

export default function ProjectLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <Protect plan={"creator"} fallback={<Subscribe />}>
      <div className="max-w-xl mx-auto">{children}</div>
    </Protect>
  );
}
