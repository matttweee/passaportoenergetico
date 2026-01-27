import React from "react";

export function Progress({ value }: { value: number }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div className="h-2 w-full rounded-full bg-zinc-800">
      <div className="h-2 rounded-full bg-white" style={{ width: `${v}%` }} />
    </div>
  );
}

