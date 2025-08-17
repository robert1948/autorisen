// client/src/context/CapeAIContext.jsx
import React, { createContext, useState, useCallback } from 'react';

export const CapeAIContext = createContext({
  isVisible: false,
  messages: [],
  onboardingStep: 0,
  onboardingData: {},
  toggleVisibility: () => {},
  addMessage: () => {},
  setOnboardingStep: () => {},
  updateOnboardingData: () => {},
});

export const CapeAIProvider = ({ children }) => {
  const [isVisible, setIsVisible] = useState(false); // Start hidden
  const [onboardingStep, setOnboardingStep] = useState(0);
  const [onboardingData, setOnboardingData] = useState({
    profileComplete: false,
    featuresViewed: false,
    aiIntroduced: false,
    dashboardTour: false,
    firstAgentLaunched: false,
  });
  
  const [messages, setMessages] = useState([
    { 
      id: 'initial-message',
      from: 'assistant', 
      text: 'Hi! I\'m CapeAI, your personal onboarding assistant. I\'m here to help you get the most out of the CapeControl platform. What would you like to explore first?',
      timestamp: new Date()
    },
  ]);

  const toggleVisibility = () => setIsVisible((prev) => !prev);

  const addMessage = useCallback((from, text) => {
    const newMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      from,
      text,
      timestamp: new Date()
    };
    setMessages((prev) => [...prev, newMessage]);
  }, []);

  const updateOnboardingData = useCallback((updates) => {
    setOnboardingData((prev) => ({ ...prev, ...updates }));
  }, []);

  const contextValue = {
    isVisible,
    messages,
    onboardingStep,
    onboardingData,
    toggleVisibility,
    addMessage,
    setOnboardingStep,
    updateOnboardingData,
  };

  return (
    <CapeAIContext.Provider value={contextValue}>
      {children}
    </CapeAIContext.Provider>
  );
};

export default CapeAIProvider;
