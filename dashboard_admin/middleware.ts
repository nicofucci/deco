import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
    const session = request.cookies.get("deco_admin_session");

    if (request.nextUrl.pathname.startsWith("/dashboard")) {
        if (!session) {
            return NextResponse.redirect(new URL("/login", request.url));
        }
    }

    if (request.nextUrl.pathname === "/") {
        if (session) {
            return NextResponse.redirect(new URL("/dashboard/overview", request.url));
        } else {
            return NextResponse.redirect(new URL("/login", request.url));
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/", "/dashboard/:path*"],
};
