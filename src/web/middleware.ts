import { auth } from "@/lib/auth";
import { createAuthClient } from "react-auth-kit";
import { NextRequest, NextResponse } from "next/server";

const authClient = createAuthClient({
  authUri: "/api/auth/token",
});

export default async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Skip auth for public routes
  if (pathname.startsWith("/login") || pathname.startsWith("/register")) {
    return NextResponse.next();
  }

  // Check auth for protected routes
  const token = authClient.getToken();
  if (!token) {
    const url = new URL("/login", req.url);
    url.searchParams.set("redirect", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next|.*\\..*).*)"],
};
