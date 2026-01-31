import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  const path = request.nextUrl.searchParams.get("path") || "";
  if (!path.startsWith("/api/")) {
    return NextResponse.json({ error: "Invalid path" }, { status: 400 });
  }
  try {
    const res = await fetch(`${BACKEND}${path}`, { headers: request.headers as HeadersInit });
    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 502 });
  }
}

export async function POST(request: NextRequest) {
  const path = request.nextUrl.searchParams.get("path") || "";
  if (!path.startsWith("/api/")) {
    return NextResponse.json({ error: "Invalid path" }, { status: 400 });
  }
  try {
    const body = await request.text();
    const res = await fetch(`${BACKEND}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...Object.fromEntries(request.headers.entries()) },
      body: body || undefined,
    });
    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 502 });
  }
}
