"use client";

interface TrendChartProps {
  userTrend: Record<string, unknown>;
  zoneTrend: Record<string, unknown>;
}

export function TrendChart({ userTrend, zoneTrend }: TrendChartProps) {
  const userDelta = (userTrend?.eur_per_kwh_delta_pct as number) ?? 0;
  const zoneDelta = (zoneTrend?.eur_per_kwh_delta_pct as number) ?? 0;

  return (
    <div className="p-4 rounded-lg bg-zinc-900 border border-zinc-800">
      <h2 className="text-sm font-medium text-zinc-400 mb-4">Trend tuo vs zona</h2>
      <div className="flex items-end gap-4 h-32">
        <div className="flex-1 flex flex-col items-center">
          <div
            className="w-full bg-emerald-500 rounded-t min-h-[4px] max-h-full"
            style={{ height: `${Math.min(100, Math.max(0, 50 + userDelta))}%` }}
          />
          <span className="text-xs text-zinc-500 mt-2">Tu</span>
        </div>
        <div className="flex-1 flex flex-col items-center">
          <div
            className="w-full bg-zinc-500 rounded-t min-h-[4px] max-h-full"
            style={{ height: `${Math.min(100, Math.max(0, 50 + zoneDelta))}%` }}
          />
          <span className="text-xs text-zinc-500 mt-2">Zona</span>
        </div>
      </div>
      <p className="text-xs text-zinc-500 mt-4">
        Variazione % €/kWh: Tu {userDelta.toFixed(1)}% · Zona {zoneDelta.toFixed(1)}%
      </p>
    </div>
  );
}
