import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const searchData = await request.json();
    
    // Call the food agent API
    const response = await fetch('http://localhost:8001/search-restaurants', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchData),
    });

    if (!response.ok) {
      throw new Error(`Food API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Food search error:', error);
    return NextResponse.json(
      { error: 'Failed to search restaurants' },
      { status: 500 }
    );
  }
}
