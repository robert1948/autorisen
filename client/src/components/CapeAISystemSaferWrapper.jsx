import React, { useEffect, useState } from 'react';
import ContextErrorBoundary from './ContextErrorBoundary';

// Dynamic import wrapper for the CapeAI system
const CapeAISystemSafe = React.lazy(() => 
  import('./CapeAISystemSafe').catch(() => {
    console.warn('Failed to load CapeAI system, using fallback');
    return { default: () => null };
  })
);

export default function CapeAISystemSaferWrapper() {
  const [shouldRender, setShouldRender] = useState(false);
  
  // Give some time for the context to be properly set up
  useEffect(() => {
    const timer = setTimeout(() => {
      setShouldRender(true);
    }, 500); // Small delay to let context providers initialize
    
    return () => clearTimeout(timer);
  }, []);
  
  if (!shouldRender) {
    return null;
  }
  
  return (
    <ContextErrorBoundary>
      <React.Suspense fallback={null}>
        <CapeAISystemSafe />
      </React.Suspense>
    </ContextErrorBoundary>
  );
}
