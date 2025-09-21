import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const searchData = await request.json();
    
    // Call the flight agent API
    const response = await fetch('http://localhost:8000/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchData),
    });

    if (!response.ok) {
      throw new Error(`Flight API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Flight search error:', error);
    return NextResponse.json(
      { error: 'Failed to search flights' },
      { status: 500 }
    );
  }
}
