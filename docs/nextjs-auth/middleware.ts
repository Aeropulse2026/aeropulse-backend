import { jwtVerify } from "jose";
import { NextRequest, NextResponse } from "next/server";

const accessCookie = "aeropulse_access";
const signingKey = new TextEncoder().encode(process.env.JWT_SIGNING_KEY);

export async function middleware(request: NextRequest) {
  const token = request.cookies.get(accessCookie)?.value;
  if (!token || !signingKey.length) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  try {
    await jwtVerify(token, signingKey, { algorithms: ["HS256"] });
    return NextResponse.next();
  } catch {
    const response = NextResponse.redirect(new URL("/login", request.url));
    response.cookies.delete(accessCookie);
    return response;
  }
}

export const config = {
  matcher: ["/dashboard/:path*", "/fleet/:path*", "/aircraft/:path*", "/maintenance/:path*", "/inventory/:path*", "/iaf-fleet/:path*"],
};
