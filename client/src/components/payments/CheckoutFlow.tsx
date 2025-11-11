/**
 * CheckoutFlow Component - Complex Multi-Step Payment Integration
 * Handles the complete checkout process with state management, validation, and error handling
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { paymentsApi } from '../../services/paymentsApi';
import { usePaymentSecurity, useSecureCheckout, usePaymentFormValidation, usePaymentAmount, usePaymentRateLimit } from '../../hooks/usePayments';
import { PaymentSecurityProvider, PaymentSecurityGuard, RateLimitDisplay } from './PaymentSecurityProvider';
import PayFastCheckout from './PayFastCheckout';
import type { 
  PaymentFlowState, 
  PaymentFlowStep, 
  PaymentFormData, 
  CheckoutRequest, 
  PayFastCheckoutResponse,
  PaymentFormValidation
} from '../../types/payments';

interface CheckoutFlowProps {
  onComplete?: (result: PayFastCheckoutResponse) => void;
  onCancel?: () => void;
  initialData?: Partial<PaymentFormData>;
  className?: string;
}

const INITIAL_FORM_DATA: PaymentFormData = {
  amount: '',
  itemName: '',
  itemDescription: '',
  customerEmail: '',
  customerFirstName: '',
  customerLastName: '',
  agreeToTerms: false,
};

const INITIAL_VALIDATION: PaymentFormValidation = {
  amount: { isValid: false, touched: false },
  itemName: { isValid: false, touched: false },
  customerEmail: { isValid: false, touched: false },
  customerFirstName: { isValid: false, touched: false },
  customerLastName: { isValid: false, touched: false },
  agreeToTerms: { isValid: false, touched: false },
};

function CheckoutFlowCore({ onComplete, onCancel, initialData, className }: CheckoutFlowProps) {
  const navigate = useNavigate();
  const { recordAttempt: recordPaymentAttempt, isBlocked } = usePaymentRateLimit();
  const { isProcessing, checkoutError, createCheckout } = useSecureCheckout();
  const { validateForm, validationResult } = usePaymentFormValidation();
  
  // Main flow state
  const [flowState, setFlowState] = useState<PaymentFlowState>({
    currentStep: 'details',
    formData: { ...INITIAL_FORM_DATA, ...initialData },
    validation: INITIAL_VALIDATION,
    isProcessing: false,
  });
  
  // Form refs for programmatic focus management
  const formRefs = {
    amount: useRef<HTMLInputElement>(null),
    itemName: useRef<HTMLInputElement>(null),
    customerEmail: useRef<HTMLInputElement>(null),
    customerFirstName: useRef<HTMLInputElement>(null),
    customerLastName: useRef<HTMLInputElement>(null),
    agreeToTerms: useRef<HTMLInputElement>(null),
  };
  
  // Amount formatting hook
  const { formattedAmount, updateAmount, amountError } = usePaymentAmount();
  
  // Auto-save form data to sessionStorage
  useEffect(() => {
    const key = 'checkoutFlow_formData';
    sessionStorage.setItem(key, JSON.stringify(flowState.formData));
  }, [flowState.formData]);
  
  // Restore form data on mount
  useEffect(() => {
    const key = 'checkoutFlow_formData';
    const saved = sessionStorage.getItem(key);
    if (saved && !initialData) {
      try {
        const parsedData = JSON.parse(saved);
        setFlowState(prev => ({
          ...prev,
          formData: { ...INITIAL_FORM_DATA, ...parsedData }
        }));
      } catch (error) {
        console.warn('Failed to restore form data:', error);
      }
    }
  }, [initialData]);
  
  // Real-time form validation
  useEffect(() => {
    const { formData } = flowState;
    
    // Convert form data to checkout request format
    const amount = parseFloat(formData.amount) || 0;
    if (amount > 0 && formData.itemName && formData.customerEmail) {
      const checkoutRequest: CheckoutRequest = {
        amount,
        itemName: formData.itemName,
        itemDescription: formData.itemDescription || undefined,
        customerEmail: formData.customerEmail,
        customerFirstName: formData.customerFirstName,
        customerLastName: formData.customerLastName,
      };
      
      validateForm(checkoutRequest);
    }
  }, [flowState.formData, validateForm]);
  
  // Update form data with validation
  const updateFormData = useCallback((field: keyof PaymentFormData, value: string | boolean) => {
    setFlowState(prev => {
      const newFormData = { ...prev.formData, [field]: value };
      const newValidation = { ...prev.validation };
      
      // Mark field as touched
      if (field in newValidation) {
        newValidation[field as keyof PaymentFormValidation] = {
          ...newValidation[field as keyof PaymentFormValidation],
          touched: true,
        };
      }
      
      // Special handling for amount field
      if (field === 'amount' && typeof value === 'string') {
        updateAmount(value);
      }
      
      return {
        ...prev,
        formData: newFormData,
        validation: newValidation,
      };
    });
  }, [updateAmount]);
  
  // Step navigation
  const goToStep = useCallback((step: PaymentFlowStep) => {
    setFlowState(prev => ({ ...prev, currentStep: step }));
  }, []);
  
  // Validate current step
  const validateCurrentStep = useCallback((): boolean => {
    const { formData, currentStep } = flowState;
    
    if (currentStep === 'details') {
      const requiredFields = ['amount', 'itemName', 'customerEmail', 'customerFirstName', 'customerLastName'];
      const hasRequiredFields = requiredFields.every(field => {
        const value = formData[field as keyof PaymentFormData];
        return typeof value === 'string' && value.trim().length > 0;
      });
      
      return hasRequiredFields && 
             formData.agreeToTerms && 
             validationResult.isValid && 
             !amountError;
    }
    
    return true;
  }, [flowState, validationResult, amountError]);
  
  // Handle step transition
  const handleNextStep = useCallback(async () => {
    if (isBlocked) {
      return; // Rate limited
    }
    
    const isValid = validateCurrentStep();
    if (!isValid) {
      // Focus on first invalid field
      const firstInvalidField = Object.keys(formRefs).find(field => {
        const validation = flowState.validation[field as keyof PaymentFormValidation];
        return validation.touched && !validation.isValid;
      });
      
      if (firstInvalidField && formRefs[firstInvalidField as keyof typeof formRefs].current) {
        formRefs[firstInvalidField as keyof typeof formRefs].current?.focus();
      }
      
      return;
    }
    
    const { currentStep, formData } = flowState;
    
    if (currentStep === 'details') {
      goToStep('review');
    } else if (currentStep === 'review') {
      await processCheckout();
    }
  }, [flowState, validateCurrentStep, isBlocked, goToStep]);
  
  // Process checkout
  const processCheckout = useCallback(async () => {
    if (isProcessing || isBlocked) return;
    
    setFlowState(prev => ({ ...prev, currentStep: 'processing', isProcessing: true }));
    
    try {
      const { formData } = flowState;
      const amount = parseFloat(formData.amount);
      
      const checkoutRequest: CheckoutRequest = {
        amount,
        itemName: formData.itemName,
        itemDescription: formData.itemDescription || undefined,
        customerEmail: formData.customerEmail,
        customerFirstName: formData.customerFirstName,
        customerLastName: formData.customerLastName,
        metadata: {
          source: 'checkout_flow',
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent.substring(0, 100),
        }
      };
      
      const response = await createCheckout(checkoutRequest);
      
      // Success
      recordPaymentAttempt(true);
      setFlowState(prev => ({
        ...prev,
        currentStep: 'success',
        checkoutData: response,
        isProcessing: false,
      }));
      
      // Clear saved form data on success
      sessionStorage.removeItem('checkoutFlow_formData');
      
      // Notify parent component
      onComplete?.(response);
      
    } catch (error) {
      // Error handling
      recordPaymentAttempt(false);
      const errorMessage = error instanceof Error ? error.message : 'Checkout failed';
      
      setFlowState(prev => ({
        ...prev,
        currentStep: 'error',
        error: errorMessage,
        isProcessing: false,
      }));
    }
  }, [flowState, isProcessing, isBlocked, createCheckout, recordPaymentAttempt, onComplete]);
  
  // Handle back navigation
  const handlePrevStep = useCallback(() => {
    const { currentStep } = flowState;
    
    if (currentStep === 'review') {
      goToStep('details');
    } else if (currentStep === 'error') {
      goToStep('review');
    }
  }, [flowState.currentStep, goToStep]);
  
  // Handle cancel
  const handleCancel = useCallback(() => {
    // Clear saved form data
    sessionStorage.removeItem('checkoutFlow_formData');
    
    if (onCancel) {
      onCancel();
    } else {
      navigate('/dashboard');
    }
  }, [onCancel, navigate]);
  
  // Handle retry after error
  const handleRetry = useCallback(() => {
    setFlowState(prev => ({
      ...prev,
      currentStep: 'review',
      error: undefined,
    }));
  }, []);
  
  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleCancel();
      } else if (event.key === 'Enter' && !isProcessing) {
        const { currentStep } = flowState;
        if (currentStep === 'details' || currentStep === 'review') {
          handleNextStep();
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [flowState.currentStep, isProcessing, handleCancel, handleNextStep]);
  
  // Render different steps
  const renderStepContent = () => {
    const { currentStep, formData, error, checkoutData } = flowState;
    
    switch (currentStep) {
      case 'details':
        return (
          <CheckoutDetailsStep
            formData={formData}
            validation={flowState.validation}
            formRefs={formRefs}
            amountError={amountError}
            formattedAmount={formattedAmount}
            validationResult={validationResult}
            onUpdateFormData={updateFormData}
            onNext={handleNextStep}
            onCancel={handleCancel}
            isValid={validateCurrentStep()}
          />
        );
        
      case 'review':
        return (
          <CheckoutReviewStep
            formData={formData}
            formattedAmount={formattedAmount}
            onConfirm={handleNextStep}
            onBack={handlePrevStep}
            onCancel={handleCancel}
            isProcessing={isProcessing}
          />
        );
        
      case 'processing':
        return <CheckoutProcessingStep />;
        
      case 'success':
        return (
          <CheckoutSuccessStep
            checkoutData={checkoutData}
            onContinue={() => navigate('/dashboard')}
          />
        );
        
      case 'error':
        return (
          <CheckoutErrorStep
            error={error || 'An unexpected error occurred'}
            onRetry={handleRetry}
            onCancel={handleCancel}
          />
        );
        
      default:
        return null;
    }
  };
  
  return (
    <div className={`checkout-flow ${className || ''}`}>
      {/* Progress indicator */}
      <CheckoutProgressIndicator currentStep={flowState.currentStep} />
      
      {/* Rate limit warning */}
      <RateLimitDisplay />
      
      {/* Main content */}
      <div className="checkout-flow__content">
        {renderStepContent()}
      </div>
    </div>
  );
}

// Main exported component with security wrapper
export default function CheckoutFlow(props: CheckoutFlowProps) {
  return (
    <PaymentSecurityProvider>
      <PaymentSecurityGuard requireSecureContext requireCSRFToken>
        <CheckoutFlowCore {...props} />
      </PaymentSecurityGuard>
    </PaymentSecurityProvider>
  );
}

// Step Components (will be detailed in separate files)
function CheckoutProgressIndicator({ currentStep }: { currentStep: PaymentFlowStep }) {
  const steps = [
    { key: 'details', label: 'Payment Details', completed: false },
    { key: 'review', label: 'Review Order', completed: false },
    { key: 'processing', label: 'Processing', completed: false },
    { key: 'success', label: 'Complete', completed: false },
  ];
  
  const currentIndex = steps.findIndex(step => step.key === currentStep);
  const completedSteps = steps.slice(0, currentIndex);
  
  return (
    <div className="checkout-progress">
      <div className="checkout-progress__steps">
        {steps.map((step, index) => (
          <div 
            key={step.key}
            className={`checkout-progress__step ${
              index <= currentIndex ? 'checkout-progress__step--active' : ''
            } ${
              index < currentIndex ? 'checkout-progress__step--completed' : ''
            }`}
          >
            <div className="checkout-progress__step-indicator">
              {index < currentIndex ? '✓' : index + 1}
            </div>
            <span className="checkout-progress__step-label">{step.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function CheckoutProcessingStep() {
  return (
    <div className="checkout-processing">
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Processing your payment...</h3>
        <p className="text-gray-600">Please wait while we prepare your secure checkout.</p>
        <p className="text-sm text-gray-500 mt-2">This may take a few moments.</p>
      </div>
    </div>
  );
}

// Export step interfaces for Codex to implement
export interface CheckoutDetailsStepProps {
  formData: PaymentFormData;
  validation: PaymentFormValidation;
  formRefs: Record<string, React.RefObject<HTMLInputElement>>;
  amountError: string | null;
  formattedAmount: string;
  validationResult: any;
  onUpdateFormData: (field: keyof PaymentFormData, value: string | boolean) => void;
  onNext: () => void;
  onCancel: () => void;
  isValid: boolean;
}

export interface CheckoutReviewStepProps {
  formData: PaymentFormData;
  formattedAmount: string;
  onConfirm: () => void;
  onBack: () => void;
  onCancel: () => void;
  isProcessing: boolean;
}

export interface CheckoutSuccessStepProps {
  checkoutData?: PayFastCheckoutResponse;
  onContinue: () => void;
}

export interface CheckoutErrorStepProps {
  error: string;
  onRetry: () => void;
  onCancel: () => void;
}

// Placeholder components for Codex to implement
function CheckoutDetailsStep(props: CheckoutDetailsStepProps) {
  return <PayFastCheckout {...props} />;
}

function CheckoutReviewStep(props: CheckoutReviewStepProps) {
  return (
    <div className="checkout-review-placeholder">
      <h3>Review Order Step</h3>
      <p>Codex: Implement review and confirmation UI</p>
    </div>
  );
}

function CheckoutSuccessStep(props: CheckoutSuccessStepProps) {
  return (
    <div className="checkout-success-placeholder">
      <h3>Success Step</h3>
      <p>Codex: Implement success state with PayFast redirect</p>
    </div>
  );
}

function CheckoutErrorStep(props: CheckoutErrorStepProps) {
  return (
    <div className="checkout-error-placeholder">
      <h3>Error Step</h3>
      <p>Codex: Implement error handling UI</p>
    </div>
  );
}
