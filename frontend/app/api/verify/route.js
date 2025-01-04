import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Create new FormData for the Python backend
    const pythonFormData = new FormData();
    pythonFormData.append('file', file);

    const response = await fetch('http://localhost:8000/api/verify', {
      method: 'POST',
      body: pythonFormData,
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Verification error:', error);
    return NextResponse.json(
      { error: 'Error processing request' },
      { status: 500 }
    );
  }
}
