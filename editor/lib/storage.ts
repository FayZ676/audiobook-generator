import "server-only";
import { promises as fs } from "fs";
import path from "path";
import type { Book, CastMember, Segment } from "./model";

// A book folder as `python -m tta_script` writes it: cast.json, and
// scripts/<chapter>.json per chapter.
const BOOKS_DIR = process.env.BOOKS_DIR ?? path.resolve(process.cwd(), "../books");

export async function listBooks(): Promise<string[]> {
  const entries = await fs.readdir(BOOKS_DIR, { withFileTypes: true }).catch(() => []);
  const books = await Promise.all(
    entries
      .filter((e) => e.isDirectory())
      .map(async (e) => ((await exists(bookPath(e.name, "cast.json"))) ? e.name : null)),
  );
  return books.filter((b): b is string => b !== null).sort();
}

export async function loadBook(name: string): Promise<Book> {
  const files = (await fs.readdir(bookPath(name, "scripts"))).filter((f) => f.endsWith(".json")).sort();
  const chapters = await Promise.all(
    files.map(async (file) => {
      const segments = await readSegments(name, file.replace(/\.json$/, ""));
      return { id: file.replace(/\.json$/, ""), title: segments[0]?.text ?? file, segments };
    }),
  );
  return { name, cast: await readCast(name), chapters };
}

export function updateSegments(book: string, chapter: string, change: (segments: Segment[]) => void) {
  return serialized(bookPath(book, "scripts", `${chapter}.json`), async (file) => {
    const segments = await readSegments(book, chapter);
    change(segments);
    await writeJson(file, { segments });
  });
}

export function updateCast(book: string, change: (cast: CastMember[]) => void) {
  return serialized(bookPath(book, "cast.json"), async (file) => {
    const cast = await readCast(book);
    change(cast);
    await writeJson(file, { members: cast });
  });
}

async function readSegments(book: string, chapter: string): Promise<Segment[]> {
  return (await readJson(bookPath(book, "scripts", `${chapter}.json`))).segments;
}

async function readCast(book: string): Promise<CastMember[]> {
  return (await readJson(bookPath(book, "cast.json"))).members;
}

export function bookPath(book: string, ...parts: string[]) {
  // Book and chapter names come from URLs; keep them inside BOOKS_DIR.
  const full = path.resolve(BOOKS_DIR, book, ...parts);
  if (!full.startsWith(BOOKS_DIR + path.sep)) throw new Error(`Bad path: ${book}/${parts.join("/")}`);
  return full;
}

// One read-modify-write at a time per file, so quick edits don't overwrite
// each other.
const queues = new Map<string, Promise<unknown>>();
function serialized(file: string, task: (file: string) => Promise<void>) {
  const next = (queues.get(file) ?? Promise.resolve()).then(() => task(file));
  queues.set(file, next.catch(() => {}));
  return next;
}

async function readJson(file: string) {
  return JSON.parse(await fs.readFile(file, "utf-8"));
}

async function writeJson(file: string, data: unknown) {
  const tmp = `${file}.tmp`;
  await fs.writeFile(tmp, JSON.stringify(data, null, 1));
  await fs.rename(tmp, file); // never leave a half-written file
}

async function exists(file: string) {
  return fs.access(file).then(
    () => true,
    () => false,
  );
}
