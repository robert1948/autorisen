// client/src/components/onboarding/OnboardingFlow.jsx
import React, { useEffect } from 'react';
import useCapeAISafe from '../../hooks/useCapeAISafe';
import { useLocation } from 'react-router-dom';

export default function OnboardingFlow() {
  const { addMessage, onboardingStep, setOnboardingStep, updateOnboardingData } = useCapeAISafe();
  const location = useLocation();

  // Define onboarding steps
  const onboardingSteps = [
    {
      id: 'welcome',
      title: 'Welcome to CapeControl',
      message: 'Welcome! I\'ll help you get started. Let\'s begin by setting up your profile.',
      trigger: () => location.pathname === '/',
      action: () => updateOnboardingData({ welcomed: true })
    },
    {
      id: 'profile_setup',
      title: 'Profile Setup',
      message: 'Great! Now let\'s complete your profile. Click on your account settings to add your business information.',
      trigger: () => location.pathname.includes('/dashboard'),
      action: () => updateOnboardingData({ profilePrompted: true })
    },
    {
      id: 'platform_tour',
      title: 'Platform Tour',
      message: 'Excellent! Now let me show you around. Here\'s your dashboard where you can manage all your AI agents and view analytics.',
      trigger: () => location.pathname === '/dashboard',
      action: () => updateOnboardingData({ dashboardTour: true })
    },
    {
      id: 'ai_agents_intro',
      title: 'AI Agents Introduction',
      message: 'Ready to explore AI agents? These are powerful tools that can help automate tasks, create content, and analyze data. Would you like to see what\'s available?',
      trigger: () => location.pathname.includes('/dashboard'),
      action: () => updateOnboardingData({ aiIntroduced: true })
    }
  ];

  useEffect(() => {
    const currentStep = onboardingSteps[onboardingStep];
    if (currentStep && currentStep.trigger()) {
      // Add onboarding message after a delay
      const timer = setTimeout(() => {
        addMessage('assistant', currentStep.message);
        currentStep.action();
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [location.pathname, onboardingStep]);

  // Auto-advance onboarding based on user actions
  useEffect(() => {
    // This could be enhanced to listen to specific user interactions
    // For now, we'll advance based on route changes
    if (location.pathname === '/dashboard' && onboardingStep < 2) {
      setOnboardingStep(2);
    }
  }, [location.pathname]);

  return null; // This component doesn't render anything visible
}

// Helper hook for triggering onboarding messages
export const useOnboardingTrigger = () => {
  const { addMessage, updateOnboardingData } = useCapeAISafe();

  const triggerHelp = (context) => {
    const helpMessages = {
      'profile': 'I see you\'re working on your profile! Make sure to add your business type and preferences so I can provide better recommendations.',
      'agents': 'Looking at AI agents? Here are some popular ones to get you started: Content Creator, Data Analyzer, and Task Automator.',
      'dashboard': 'This is your command center! From here you can monitor all your AI agents, view usage analytics, and manage your account.',
      'billing': 'Questions about pricing? We offer transparent, usage-based pricing. Most users start with our free tier and upgrade as they grow.',
    };

    if (helpMessages[context]) {
      addMessage('assistant', helpMessages[context]);
      updateOnboardingData({ [`${context}HelpShown`]: true });
    }
  };

  return { triggerHelp };
};
