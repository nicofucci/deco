import { NextRequest, NextResponse } from "next/server";

const ORCHESTRATOR_URL =
    process.env.ORCHESTRATOR_INTERNAL_URL ||
    process.env.ORCHESTRATOR_URL ||
    "http://deco-sec-orchestrator:8000";

export async function GET(req: NextRequest) {
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

    const { searchParams } = new URL(req.url);
    const assetId = searchParams.get("asset_id");
    const upstream = `${ORCHESTRATOR_URL}/api/client/findings${assetId ? `?asset_id=${assetId}` : ""}`;

    const res = await fetch(upstream, {
        headers: { "X-Client-API-Key": apiKey },
        cache: "no-store",
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
}
