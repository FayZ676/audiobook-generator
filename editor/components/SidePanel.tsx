"use client";

/** A side bar: the same on either side. It runs the full height beside the
 * book on wide screens and drops over it, below the header, on narrow ones.
 * It opens from its button at that end of the header, has one
 * quiet line at its top, and holds rows made with SideRow. */
export default function SidePanel({
  side,
  open,
  head,
  children,
}: {
  side: "left" | "right";
  open: boolean;
  head: React.ReactNode; // one line: what's here, and at most a mark to act on it
  children: React.ReactNode;
}) {
  return (
    // Slides in from its edge; hidden once out, so it can't be tabbed into.
    <aside
      aria-hidden={!open}
      className={`fixed bottom-0 top-12 z-30 flex w-80 max-w-[85vw] flex-col border-line bg-bg shadow-2xl transition-[translate,visibility] duration-300 ease-out motion-reduce:transition-none xl:top-0 xl:shadow-none ${
        side === "left" ? "left-0 border-r" : "right-0 border-l"
      } ${open ? "visible translate-x-0" : `invisible ${side === "left" ? "-translate-x-full" : "translate-x-full"}`}`}
    >
      <div className="flex h-12 shrink-0 items-center gap-2 px-5 text-xs text-muted">{head}</div>
      <div className="flex-1 overflow-y-auto pb-6">{children}</div>
    </aside>
  );
}

/** A row in a side bar: chosen rows are tinted the same on both sides. */
export function SideRow({
  id,
  chosen,
  onClick,
  children,
  below,
}: {
  id?: string;
  chosen: boolean;
  onClick: () => void;
  children: React.ReactNode; // the row's one line
  below?: React.ReactNode; // details under it, if any
}) {
  return (
    <div id={id} className={`px-5 py-1.5 transition-colors ${chosen ? "bg-accent/10" : "hover:bg-ink/[0.035]"}`}>
      <button onClick={onClick} className="flex w-full items-center gap-2.5 text-left">
        {children}
      </button>
      {below}
    </div>
  );
}

/** The button for a side bar, at that end of the header: a page with that
 * side's bar drawn in, filled while the bar is open. */
export function SideToggle({ side, open, onClick, title }: { side: "left" | "right"; open: boolean; onClick: () => void; title: string }) {
  return (
    <button
      onClick={onClick}
      title={title}
      aria-pressed={open}
      className={`flex h-12 shrink-0 items-center px-2 transition-colors ${
        open ? "text-ink" : "text-muted hover:text-ink"
      }`}
    >
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.3" aria-hidden>
        <rect x="1.5" y="2.5" width="15" height="13" rx="2.5" />
        <path d={side === "left" ? "M6.5 2.5v13" : "M11.5 2.5v13"} />
        {open && <rect x={side === "left" ? 1.5 : 11.5} y="2.5" width="5" height="13" fill="currentColor" opacity="0.18" stroke="none" />}
      </svg>
    </button>
  );
}
