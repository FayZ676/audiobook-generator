import "server-only";
import { execFile } from "child_process";
import path from "path";
import { promisify } from "util";
import { bookPath } from "./storage";

// The script package's command line does the asking (python -m tta_script recheck).
const SCRIPT_DIR = process.env.SCRIPT_DIR ?? path.resolve(process.cwd(), "../script");
const PYTHON = path.join(SCRIPT_DIR, ".venv/bin/python");

/** Claude Opus's speaker for each segment id asked about, or for every
 * unreviewed dialogue line of the chapter when none are given. */
export async function recheck(book: string, chapter: string, segmentIds: string[]): Promise<Record<string, string>> {
  const bad = segmentIds.filter((id) => !/^seg-\d+$/.test(id));
  if (bad.length) throw new Error(`Bad segment ids: ${bad.join(", ")}`);
  bookPath(book, "scripts", `${chapter}.json`); // throws on a path outside the books folder
  const { stdout } = await promisify(execFile)(
    PYTHON,
    ["-m", "tta_script", "recheck", bookPath(book), chapter, ...segmentIds],
    { cwd: SCRIPT_DIR, timeout: 10 * 60_000, maxBuffer: 10 * 1024 * 1024 },
  );
  return JSON.parse(stdout);
}
