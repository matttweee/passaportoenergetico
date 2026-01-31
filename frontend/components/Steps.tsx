"use client";

interface StepsProps {
  current: number;
  steps: string[];
}

export function Steps({ current, steps }: StepsProps) {
  return (
    <div className="flex items-center gap-2 mb-8">
      {steps.map((label, i) => (
        <div key={i} className="flex items-center gap-2">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              i < current ? "bg-emerald-600 text-white" : i === current ? "bg-zinc-600 text-white" : "bg-zinc-800 text-zinc-500"
            }`}
          >
            {i + 1}
          </div>
          <span className={i <= current ? "text-zinc-300" : "text-zinc-500"}>{label}</span>
          {i < steps.length - 1 && <span className="text-zinc-600 mx-1">→</span>}
        </div>
      ))}
    </div>
  );
}
