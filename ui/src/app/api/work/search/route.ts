import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const searchData = await request.json();
    
    // Call the work agent API
    const response = await fetch('http://localhost:8005/search-jobs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchData),
    });

    if (!response.ok) {
      throw new Error(`Work API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Work search error:', error);
    return NextResponse.json(
      { error: 'Failed to search jobs' },
      { status: 500 }
    );
  }
}
