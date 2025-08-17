import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import useCapeAISafe from './useCapeAISafe';

// Onboarding steps configuration
const ONBOARDING_STEPS = {
  welcome: {
    id: 'welcome',
    title: 'Welcome to CapeControl!',
    description: 'Let me help you get started with our AI-powered platform',
    triggers: ['/'],
    nextStep: 'profile',
    autoTrigger: true
  },
  profile: {
    id: 'profile',
    title: 'Complete Your Profile',
    description: 'Set up your business profile to get personalized recommendations',
    triggers: ['/profile', '/'],
    nextStep: 'features',
    completionCheck: (data) => data.profileComplete
  },
  features: {
    id: 'features',
    title: 'Explore Platform Features',
    description: 'Learn about our AI agents and capabilities',
    triggers: ['/features', '/dashboard'],
    nextStep: 'assistant',
    completionCheck: (data) => data.featuresViewed
  },
  assistant: {
    id: 'assistant',
    title: 'Meet Your AI Assistant',
    description: 'Get to know CapeAI and how it can help you',
    triggers: ['*'], // Available everywhere
    nextStep: 'dashboard',
    completionCheck: (data) => data.aiIntroduced
  },
  dashboard: {
    id: 'dashboard',
    title: 'Explore Your Dashboard',
    description: 'Tour your control center for managing AI agents',
    triggers: ['/dashboard'],
    nextStep: 'agent',
    completionCheck: (data) => data.dashboardTour
  },
  agent: {
    id: 'agent',
    title: 'Launch Your First Agent',
    description: 'Try out an AI agent to see the platform in action',
    triggers: ['/agents', '/dashboard'],
    nextStep: 'complete',
    completionCheck: (data) => data.firstAgentLaunched
  },
  complete: {
    id: 'complete',
    title: 'Onboarding Complete!',
    description: 'You\'re ready to explore the full power of CapeControl',
    triggers: [],
    nextStep: null,
    completionCheck: () => true
  }
};

export default function useOnboarding() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // ✅ ALL hook calls must be at the top level before any conditional logic
  const capeAIData = useCapeAISafe();
  const [currentStep, setCurrentStep] = useState('welcome');
  const [showStepDialog, setShowStepDialog] = useState(false);
  const [stepHistory, setStepHistory] = useState([]);
  
  // ✅ useEffect calls must also be at the top level
  useEffect(() => {
    // Handle route changes for step triggering
    if (capeAIData) {
      const triggerStepForRoute = (pathname) => {
        // Route-based step logic can go here
        console.log('Route changed:', pathname);
      };
      triggerStepForRoute(location.pathname);
    }
  }, [location.pathname, capeAIData]);

  useEffect(() => {
    // Track step history
    if (currentStep && !stepHistory.includes(currentStep)) {
      setStepHistory(prev => [...prev, currentStep]);
    }
  }, [currentStep, stepHistory]);
  
  // Safe fallback if context is not available
  if (!capeAIData) {
    // Return safe defaults if context is not available
    return {
      currentStep: 'welcome',
      showContextualHelp: false,
      isComplete: false,
      getCurrentStepConfig: () => ONBOARDING_STEPS['welcome'],
      nextStep: () => {},
      previousStep: () => {},
      completeStep: () => {},
      completeCurrentStep: () => {},
      goToStep: () => {},
      showStepDialog: false,
      setShowStepDialog: () => {},
      isStepCompleted: () => false,
      getProgress: () => ({ completed: 0, total: 6, percentage: 0 }),
      showContextualMessage: () => {}
    };
  }
  
  const { 
    onboardingData, 
    updateOnboardingData, 
    onboardingStep,
    addMessage,
    toggleVisibility 
  } = capeAIData;

  // Update current step from context if available
  if (onboardingStep && currentStep !== onboardingStep) {
    setCurrentStep(onboardingStep);
  }

  // Get current step configuration
  const getCurrentStepConfig = () => ONBOARDING_STEPS[currentStep];

  // Check if current step is completed
  const isStepCompleted = (stepId) => {
    const step = ONBOARDING_STEPS[stepId];
    if (!step.completionCheck) return false;
    return step.completionCheck(onboardingData);
  };

  // Calculate overall progress
  const getOverallProgress = () => {
    const totalSteps = Object.keys(ONBOARDING_STEPS).length - 1; // Exclude 'complete'
    const completedSteps = Object.keys(ONBOARDING_STEPS)
      .filter(stepId => stepId !== 'complete' && isStepCompleted(stepId))
      .length;
    
    return {
      completed: completedSteps,
      total: totalSteps,
      percentage: Math.round((completedSteps / totalSteps) * 100)
    };
  };

  // Mark step as completed and move to next
  const completeStep = (stepId, data = {}) => {
    const updatedData = { ...onboardingData, ...data };
    
    // Mark specific step completion flags
    const stepCompletionFlags = {
      profile: { profileComplete: true },
      features: { featuresViewed: true },
      assistant: { aiIntroduced: true },
      dashboard: { dashboardTour: true },
      agent: { firstAgentLaunched: true }
    };

    if (stepCompletionFlags[stepId]) {
      Object.assign(updatedData, stepCompletionFlags[stepId]);
    }

    updateOnboardingData(updatedData);

    // Move to next step
    const currentConfig = ONBOARDING_STEPS[stepId];
    if (currentConfig?.nextStep && currentConfig.nextStep !== 'complete') {
      setCurrentStep(currentConfig.nextStep);
    } else if (currentConfig?.nextStep === 'complete') {
      setCurrentStep('complete');
      // Celebration message
      addMessage('assistant', '🎉 Congratulations! You\'ve completed the onboarding process. You\'re now ready to explore the full power of CapeControl!');
    }
  };

  // Trigger step based on current route
  const triggerStepForRoute = (path) => {
    const availableSteps = Object.values(ONBOARDING_STEPS).filter(step => {
      return step.triggers.includes(path) || step.triggers.includes('*');
    });

    // Find the next incomplete step that matches this route
    const nextStep = availableSteps.find(step => 
      !isStepCompleted(step.id) && step.id !== 'complete'
    );

    if (nextStep && nextStep.id !== currentStep) {
      setCurrentStep(nextStep.id);
      
      // Auto-trigger help for certain steps
      if (nextStep.autoTrigger) {
        setTimeout(() => {
          showContextualHelp(nextStep.id);
        }, 1000);
      }
    }
  };

  // Show contextual help for current step
  const showContextualHelp = (stepId = currentStep) => {
    const step = ONBOARDING_STEPS[stepId];
    if (!step) return;

    const helpMessages = {
      welcome: 'Welcome to CapeControl! I\'m CapeAI, your personal assistant. I\'ll help you get started with our AI-powered platform. Would you like me to show you around?',
      profile: 'Let\'s set up your profile first! This helps me provide better, more personalized assistance. What type of business are you running?',
      features: 'Now let me show you our amazing features! We have AI agents for automation, content creation, data analysis, and more. Which area interests you most?',
      assistant: 'Hi there! I\'m CapeAI, and I\'m here to help you succeed. I can answer questions, provide guidance, and help you make the most of our platform. What would you like to know?',
      dashboard: 'Welcome to your dashboard! This is your command center where you can monitor your AI agents, view analytics, and manage your account. Let me give you a quick tour.',
      agent: 'Ready to launch your first AI agent? I can recommend the best one based on your business needs. What kind of tasks would you like to automate?'
    };

    if (helpMessages[stepId]) {
      addMessage('assistant', helpMessages[stepId]);
      toggleVisibility(); // Open chat if closed
    }
  };

  // Skip current step
  const skipStep = () => {
    const currentConfig = getCurrentStepConfig();
    if (currentConfig?.nextStep) {
      setCurrentStep(currentConfig.nextStep);
    }
  };

  // Go to specific step
  const goToStep = (stepId) => {
    if (ONBOARDING_STEPS[stepId]) {
      setCurrentStep(stepId);
      showContextualHelp(stepId);
    }
  };

  // Navigate to relevant page for current step
  const navigateToStepPage = () => {
    const navigationMap = {
      profile: '/profile',
      features: '/features',
      dashboard: '/dashboard',
      agent: '/agents'
    };

    const targetPath = navigationMap[currentStep];
    if (targetPath && location.pathname !== targetPath) {
      navigate(targetPath);
    }
  };

  // Reset onboarding (for testing or restart)
  const resetOnboarding = () => {
    setCurrentStep('welcome');
    updateOnboardingData({
      profileComplete: false,
      featuresViewed: false,
      aiIntroduced: false,
      dashboardTour: false,
      firstAgentLaunched: false
    });
    setStepHistory([]);
  };

  // Check if onboarding is complete
  const isOnboardingComplete = () => {
    return currentStep === 'complete' || getOverallProgress().percentage === 100;
  };

  return {
    // Current state
    currentStep,
    currentStepConfig: getCurrentStepConfig(),
    isComplete: isOnboardingComplete(),
    progress: getOverallProgress(),
    
    // Step management
    completeStep,
    skipStep,
    goToStep,
    navigateToStepPage,
    resetOnboarding,
    
    // Helper functions
    showContextualHelp,
    isStepCompleted,
    triggerStepForRoute,
    
    // Step dialog management
    showStepDialog,
    setShowStepDialog,
    
    // History
    stepHistory,
    
    // All steps configuration (for building UI)
    allSteps: ONBOARDING_STEPS
  };
}
