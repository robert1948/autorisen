import { useContext } from 'react';
import { CapeAIContext } from '../context/CapeAIContextSafe';

export default function useCapeAISafe() {
  // Safe fallback object
  const safeDefaults = {
    isVisible: false,
    messages: [],
    onboardingStep: 0,
    onboardingData: {
      profileComplete: false,
      featuresViewed: false,
      aiIntroduced: false,
      dashboardTour: false,
      firstAgentLaunched: false,
    },
    toggleVisibility: () => console.debug('CapeAI not available'),
    addMessage: () => console.debug('CapeAI not available'),
    setOnboardingStep: () => console.debug('CapeAI not available'),
    updateOnboardingData: () => console.debug('CapeAI not available'),
    isInitialized: false,
  };
  
  try {
    const context = useContext(CapeAIContext);
    
    // If no context provider or context is not properly initialized, return safe defaults
    if (!context || typeof context.isInitialized === 'undefined' || !context.isInitialized) {
      return safeDefaults;
    }
    
    return context;
  } catch (error) {
    console.warn('CapeAI context error:', error);
    return safeDefaults;
  }
}
