import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const OnboardingGuide: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: "Welcome to CapeControl",
      content: (
        <div className="text-center">
          <div className="mx-auto h-24 w-24 bg-blue-100 rounded-full flex items-center justify-center mb-6">
            <svg className="h-12 w-12 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Powerful AI Agents at Your Fingertips
          </h2>
          <p className="text-gray-600">
            CapeControl helps you automate tasks, streamline workflows, and boost productivity with intelligent AI agents.
          </p>
        </div>
      )
    },
    {
      title: "Choose Your Path",
      content: (
        <div className="text-center">
          <div className="mx-auto h-24 w-24 bg-purple-100 rounded-full flex items-center justify-center mb-6">
            <svg className="h-12 w-12 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            What Would You Like to Do?
          </h2>
          <div className="space-y-4 mt-6">
            <Link
              to="/onboarding/customer"
              className="block w-full p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 transition-colors"
            >
              <div className="flex items-center">
                <div className="flex-shrink-0 h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-green-600 font-semibold">👤</span>
                </div>
                <div className="ml-4 text-left">
                  <h3 className="text-lg font-medium text-gray-900">Use AI Agents</h3>
                  <p className="text-gray-500 text-sm">Automate tasks and boost productivity</p>
                </div>
              </div>
            </Link>
            <Link
              to="/onboarding/developer"
              className="block w-full p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 transition-colors"
            >
              <div className="flex items-center">
                <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-blue-600 font-semibold">⚡</span>
                </div>
                <div className="ml-4 text-left">
                  <h3 className="text-lg font-medium text-gray-900">Build AI Agents</h3>
                  <p className="text-gray-500 text-sm">Create and share your own agents</p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      )
    },
    {
      title: "Get Started",
      content: (
        <div className="text-center">
          <div className="mx-auto h-24 w-24 bg-green-100 rounded-full flex items-center justify-center mb-6">
            <svg className="h-12 w-12 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            You're All Set!
          </h2>
          <p className="text-gray-600 mb-6">
            Ready to explore the power of AI agents? Let's dive into your personalized onboarding experience.
          </p>
          <button
            onClick={() => navigate('/onboarding/checklist')}
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
          >
            Continue to Checklist
          </button>
        </div>
      )
    }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8 mx-4">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>Step {currentStep + 1} of {steps.length}</span>
            <span>{Math.round(((currentStep + 1) / steps.length) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="mb-8 min-h-[400px] flex items-center">
          {steps[currentStep].content}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          {currentStep < steps.length - 1 && (
            <button
              onClick={nextStep}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Next
            </button>
          )}
          
          <Link
            to="/dashboard"
            className="px-6 py-2 text-gray-500 hover:text-gray-700"
          >
            Skip Guide
          </Link>
        </div>
      </div>
    </div>
  );
};

export default OnboardingGuide;