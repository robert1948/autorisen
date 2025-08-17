import React, { useEffect, Suspense } from 'react';
import { useLocation } from 'react-router-dom';
import ContextErrorBoundary from './ContextErrorBoundary';
import useCapeAISafe from '../hooks/useCapeAISafe';

// Lazy load components to prevent initial render issues
const CapeAIFloatingButton = React.lazy(() => import('./CapeAIFloatingButton'));
const OnboardingFlow = React.lazy(() => import('./onboarding/OnboardingFlow'));

function CapeAISystemInner() {
  const location = useLocation();
  const { isInitialized, addMessage, isVisible } = useCapeAISafe();

  // Only run effects after initialization
  useEffect(() => {
    if (!isInitialized) return;

    // Handle route-based contextual messages with safe delay
    const routeMessages = {
      '/dashboard': 'Welcome to your dashboard! This is where you can monitor and manage all your AI agents.',
      '/profile': 'Let\'s get your profile set up! This helps me provide better assistance tailored to your business.',
      '/agents': 'Ready to explore AI agents? I can help you find the perfect agent for your needs.',
    };

    const message = routeMessages[location.pathname];
    if (message && !isVisible) {
      // Safely delay the message
      const timer = setTimeout(() => {
        try {
          addMessage('assistant', message);
        } catch (error) {
          console.warn('Error adding route message:', error);
        }
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, [location.pathname, isInitialized, isVisible, addMessage]);

  // Don't render until initialized
  if (!isInitialized) {
    return null;
  }

  return (
    <Suspense fallback={null}>
      <ContextErrorBoundary>
        <CapeAIFloatingButton />
      </ContextErrorBoundary>
    </Suspense>
  );
}

export default function CapeAISystemSafe() {
  return (
    <ContextErrorBoundary>
      <CapeAISystemInner />
    </ContextErrorBoundary>
  );
}
