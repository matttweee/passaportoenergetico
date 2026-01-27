import React from "react";

export function Card({
  title,
  children,
  className
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={"rounded-2xl border border-zinc-800 bg-zinc-900/40 p-5 " + (className ?? "")}>
      {title ? <div className="mb-3 text-sm font-semibold text-zinc-200">{title}</div> : null}
      {children}
    </div>
  );
}

