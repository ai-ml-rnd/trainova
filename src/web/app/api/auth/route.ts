import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get("code");

  if (!code) {
    return NextResponse.json({ error: "Missing code parameter" }, { status: 400 });
  }

  try {
    // Exchange code for tokens
    const response = await fetch(`${process.env.API_URL}/v1/auth/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error("Failed to exchange code for tokens");
    }

    const data = await response.json();

    // Set cookies (HttpOnly, Secure in production)
    const refreshTokenCookie = `refresh_token=${data.refresh_token}; HttpOnly; Path=/; ${process.env.NODE_ENV === "production" ? "Secure; " : ""}SameSite=Strict`;
    const accessTokenCookie = `access_token=${data.access_token}; HttpOnly; Path=/; ${process.env.NODE_ENV === "production" ? "Secure; " : ""}SameSite=Strict`;

    const responseObj = NextResponse.json(data);
    responseObj.headers.set("Set-Cookie", refreshTokenCookie);
    responseObj.headers.set("Set-Cookie", accessTokenCookie);

    return responseObj;
  } catch (error) {
    return NextResponse.json({ error: "Authentication failed" }, { status: 500 });
  }
}
