import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import CapeAIFloatingButton from './CapeAIFloatingButton';
import OnboardingFlow from './onboarding/OnboardingFlow';
import useOnboarding from '../hooks/useOnboarding';
import useCapeAISafe from '../hooks/useCapeAISafe';

export default function CapeAISystem() {
  const location = useLocation();
  
  // ✅ ALL hook calls are now completely unconditional at the top level
  const onboardingData = useOnboarding();
  const capeAIData = useCapeAISafe();
  
  // ✅ useEffect calls must also be at the top level
  useEffect(() => {
    if (onboardingData && capeAIData && !onboardingData.isComplete) {
      const routeMessages = {
        '/dashboard': 'Welcome to your dashboard! This is where you can monitor and manage all your AI agents.',
        '/profile': 'Let\'s get your profile set up! This helps me provide better assistance tailored to your business.',
        '/agents': 'Ready to explore AI agents? I can help you find the perfect agent for your needs.',
        '/settings': 'Need help with settings? I can guide you through the configuration options.',
        '/features': 'Let me show you our amazing platform features and how they can benefit your business!'
      };

      const message = routeMessages[location.pathname];
      if (message && !capeAIData.isVisible) {
        const timer = setTimeout(() => {
          capeAIData.addMessage('assistant', message);
        }, 1000);
        
        return () => clearTimeout(timer);
      }
    }
  }, [location.pathname, onboardingData?.isComplete, capeAIData?.isVisible, capeAIData?.addMessage]);

  useEffect(() => {
    if (onboardingData && capeAIData) {
      const { currentStep, showContextualHelp } = onboardingData;
      const { addMessage } = capeAIData;
      
      if (showContextualHelp) {
        const helpMessages = {
          'profile': 'Fill out your business profile to get personalized AI recommendations.',
          'agents': 'Browse our marketplace to find AI agents that match your needs.',
          'dashboard': 'Monitor your AI agents performance and track your business metrics.',
          'complete': 'Congratulations! You\'re all set up. Feel free to ask me anything!'
        };
        
        const message = helpMessages[currentStep];
        if (message) {
          addMessage('assistant', message);
        }
      }
    }
  }, [onboardingData?.currentStep, onboardingData?.showContextualHelp, capeAIData?.addMessage]);
  
  // Safe fallback if context is not available
  if (!onboardingData || !capeAIData) {
    return null;
  }
  
  const { currentStep, showContextualHelp, isComplete } = onboardingData;

  return (
    <div className="cape-ai-system">
      {/* Onboarding Flow */}
      {!isComplete && (
        <OnboardingFlow 
          currentStep={currentStep}
          showContextualHelp={showContextualHelp}
        />
      )}
      
      {/* Floating AI Button */}
      <CapeAIFloatingButton />
    </div>
  );
}
