import { PricingTable } from "@clerk/nextjs";

export default function Subscribe() {
  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "0 1rem" }}>
      <PricingTable />
    </div>
  );
}
