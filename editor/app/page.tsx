import Link from "next/link";
import { listBooks } from "@/lib/storage";

export default async function Home() {
  const books = await listBooks();
  return (
    <main className="mx-auto max-w-xl px-6 py-24">
      <h1 className="text-sm font-medium text-muted">Script editor</h1>
      <h2 className="mt-1 text-2xl font-semibold tracking-tight">Books</h2>
      {books.length === 0 ? (
        <p className="mt-8 text-sm leading-6 text-muted">
          No books yet. Put a book&apos;s chapters in <code className="font-mono">books/&lt;name&gt;/chapters/</code>{" "}
          and run <code className="font-mono">python -m tta_script ../books/&lt;name&gt;</code> from{" "}
          <code className="font-mono">script/</code>.
        </p>
      ) : (
        <ul className="mt-8 divide-y divide-line border-y border-line">
          {books.map((book) => (
            <li key={book}>
              <Link
                href={`/${encodeURIComponent(book)}`}
                className="flex items-center justify-between py-4 text-[15px] transition-colors hover:text-accent"
              >
                {book}
                <span className="text-muted">→</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
