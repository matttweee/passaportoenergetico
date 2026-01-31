"use client";

interface MapPreviewProps {
  zoneKey: string;
  points: Array<{ lat: number; lng: number; color: string }>;
  coverageOpacity: number;
}

export function MapPreview({ zoneKey, points, coverageOpacity }: MapPreviewProps) {
  return (
    <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
      <h2 className="text-sm font-medium text-zinc-400 mb-2">Mappa zona {zoneKey}</h2>
      <div
        className="h-48 rounded bg-zinc-800 relative"
        style={{ opacity: Math.max(0.2, coverageOpacity) }}
      >
        {points.slice(0, 20).map((p, i) => (
          <div
            key={i}
            className="absolute w-2 h-2 rounded-full bg-emerald-500"
            style={{
              left: `${50 + (p.lng % 10)}%`,
              top: `${50 + (p.lat % 10)}%`,
              backgroundColor: p.color === "green" ? "#10b981" : p.color === "yellow" ? "#f59e0b" : "#ef4444",
            }}
          />
        ))}
      </div>
      <p className="text-xs text-zinc-500 mt-2">{points.length} punti in zona</p>
    </div>
  );
}
