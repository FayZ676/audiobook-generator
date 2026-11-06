import { notFound } from "next/navigation";
import BookEditor from "@/components/BookEditor";
import { loadBook } from "@/lib/storage";

export const dynamic = "force-dynamic"; // always read the files as they are now

export default async function BookPage({
  params,
  searchParams,
}: {
  params: Promise<{ book: string }>;
  searchParams: Promise<{ view?: string }>;
}) {
  const { book } = await params;
  const { view } = await searchParams;
  const loaded = await loadBook(decodeURIComponent(book)).catch(() => null);
  if (!loaded) notFound();
  return <BookEditor initial={loaded} initialView={view} />;
}
