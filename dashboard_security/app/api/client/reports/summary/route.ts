import { NextRequest, NextResponse } from "next/server";

const ORCHESTRATOR_URL =
    process.env.ORCHESTRATOR_INTERNAL_URL ||
    process.env.ORCHESTRATOR_URL ||
    "http://deco-sec-orchestrator:8000";

export async function POST(req: NextRequest) {
    const apiKey =
        req.headers.get("x-client-api-key") ||
        req.headers.get("X-Client-API-Key") ||
        req.headers.get("x-api-key");

    if (!apiKey) {
        return NextResponse.json(
            { detail: "Falta X-Client-API-Key" },
            { status: 401 }
        );
    }

    const body = await req.json().catch(() => ({}));
    const upstream = `${ORCHESTRATOR_URL}/api/client/reports/summary`;
    const res = await fetch(upstream, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Client-API-Key": apiKey,
        },
        body: JSON.stringify(body || {}),
        cache: "no-store",
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
}
