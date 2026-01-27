import React from "react";

type Variant = "primary" | "secondary" | "danger";

export function Button({
  children,
  onClick,
  type = "button",
  disabled,
  variant = "primary",
  className
}: {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
  variant?: Variant;
  className?: string;
}) {
  const base =
    "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-zinc-950 disabled:opacity-50 disabled:cursor-not-allowed";
  const styles =
    variant === "primary"
      ? "bg-white text-zinc-950 hover:bg-zinc-100 focus:ring-white"
      : variant === "danger"
        ? "bg-red-500 text-white hover:bg-red-600 focus:ring-red-500"
        : "bg-zinc-800 text-zinc-50 hover:bg-zinc-700 focus:ring-zinc-300";
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={`${base} ${styles} ${className ?? ""}`}>
      {children}
    </button>
  );
}

