import { NextRequest, NextResponse } from "next/server";

const COMMUTE_AGENT_URL = "http://localhost:8006";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${COMMUTE_AGENT_URL}/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: "Commute Agent error", details: errorData.detail },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Commute API error:", error);
    return NextResponse.json(
      { error: "Internal proxy error", details: "fetch failed" },
      { status: 500 }
    );
  }
}
