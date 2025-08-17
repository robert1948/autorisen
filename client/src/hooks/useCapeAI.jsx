import { useContext } from 'react';
import { CapeAIContext } from '../context/CapeAIContextSafe';

export default function useCapeAI() {
  const context = useContext(CapeAIContext);
  
  if (!context) {
    console.warn('useCapeAI: Context not available, returning safe defaults');
    return {
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
      toggleVisibility: () => {},
      addMessage: () => {},
      setOnboardingStep: () => {},
      updateOnboardingData: () => {},
      isInitialized: false,
    };
  }
  
  return context;
}
