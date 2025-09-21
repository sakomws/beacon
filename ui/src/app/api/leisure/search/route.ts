import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const searchData = await request.json();
    
    // Call the leisure agent API
    const response = await fetch('http://localhost:8002/search-activities', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchData),
    });

    if (!response.ok) {
      throw new Error(`Leisure API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Leisure search error:', error);
    return NextResponse.json(
      { error: 'Failed to search activities' },
      { status: 500 }
    );
  }
}
