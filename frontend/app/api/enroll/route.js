import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');
    const employeeId = formData.get('employeeId');

    if (!file || !employeeId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Create new FormData for the Python backend
    const pythonFormData = new FormData();
    pythonFormData.append('file', file);
    pythonFormData.append('employeeId', employeeId);

    const response = await fetch('http://localhost:8000/api/enroll', {
      method: 'POST',
      body: pythonFormData,
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Enrollment error:', error);
    return NextResponse.json(
      { error: 'Error processing request' },
      { status: 500 }
    );
  }
}