"use client";

import { useState } from "react";
import ProctoringSystem from "./components/ProctoringSystem";
import { Button } from '@/components/ui/button';

export default function Home() {
  const [showProctoringSystem, setShowProctoringSystem] = useState(false);

  if (showProctoringSystem) {
    return (
      <main className="min-h-screen p-8">
        <ProctoringSystem />
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8 flex flex-col items-center justify-center space-y-4">
      <Button onClick={() => setShowProctoringSystem(true)}>Enroll/Verify</Button>
      <Button onClick={() => {}}>Office Mode</Button>
    </main>
  );
}
