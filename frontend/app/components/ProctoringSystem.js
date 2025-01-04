"use client"
import React, { useState } from 'react';
import { Upload, UserPlus, UserCheck } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';

const ProctoringSystem = () => {
  const [employeeId, setEmployeeId] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState('enroll'); // 'enroll' or 'verify'

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('file', selectedFile);
    
    if (mode === 'enroll') {
      formData.append('employeeId', employeeId);
      
      try {
        const response = await fetch('/api/enroll', {
          method: 'POST',
          body: formData,
        });
        
        const data = await response.json();
        setMessage(data.message);
      } catch (error) {
        setMessage('Error enrolling employee');
      }
    } else {
      try {
        const response = await fetch('/api/verify', {
          method: 'POST',
          body: formData,
        });
        
        const data = await response.json();
        setMessage(data.matched ? `Matched ID: ${data.employeeId}` : 'No match found');
      } catch (error) {
        setMessage('Error verifying face');
      }
    }
    
    setIsLoading(false);
    setSelectedFile(null);
    setEmployeeId('');
  };

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Face Recognition System</CardTitle>
            <CardDescription>
              {mode === 'enroll' ? 'Enroll new employee' : 'Verify employee identity'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex space-x-4">
                <Button 
                  onClick={() => setMode('enroll')} 
                  variant={mode === 'enroll' ? 'default' : 'outline'}
                  className="flex-1"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Enroll
                </Button>
                <Button 
                  onClick={() => setMode('verify')} 
                  variant={mode === 'verify' ? 'default' : 'outline'}
                  className="flex-1"
                >
                  <UserCheck className="w-4 h-4 mr-2" />
                  Verify
                </Button>
              </div>

              {mode === 'enroll' && (
                <Input
                  placeholder="Enter Employee ID"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  className="w-full"
                />
              )}

              <div className="flex flex-col items-center space-y-4">
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="w-full"
                />
                
                {selectedFile && (
                  <img
                    src={URL.createObjectURL(selectedFile)}
                    alt="Preview"
                    className="max-w-xs rounded-lg shadow-md"
                  />
                )}

                <Button 
                  onClick={handleSubmit}
                  disabled={!selectedFile || (mode === 'enroll' && !employeeId) || isLoading}
                  className="w-full"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  {isLoading ? 'Processing...' : mode === 'enroll' ? 'Enroll Employee' : 'Verify Identity'}
                </Button>
              </div>

              {message && (
                <Alert>
                  <AlertDescription>{message}</AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProctoringSystem;