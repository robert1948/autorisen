/**
 * Payment Security Hooks
 * React hooks for secure payment form handling with validation
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { paymentsApi, PaymentSecurityValidator, CSRFTokenManager, type CheckoutRequest, type PaymentValidationResult } from '../services/paymentsApi';

// Security context hook
export function usePaymentSecurity() {
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const [isSecureContext, setIsSecureContext] = useState(false);
  const [securityErrors, setSecurityErrors] = useState<string[]>([]);
  
  useEffect(() => {
    // Check if running in secure context
    const isSecure = window.location.protocol === 'https:' || 
                    window.location.hostname === 'localhost' ||
                    window.location.hostname === '127.0.0.1';
    setIsSecureContext(isSecure);
    
    if (!isSecure) {
      setSecurityErrors(['Payment forms require a secure connection']);
    }
  }, []);
  
  const refreshCSRFToken = useCallback(async () => {
    try {
      const token = await CSRFTokenManager.getToken();
      setCsrfToken(token);
      setSecurityErrors(prev => prev.filter(error => !error.includes('CSRF')));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'CSRF token error';
      setSecurityErrors(prev => [...prev.filter(error => !error.includes('CSRF')), errorMessage]);
    }
  }, []);
  
  useEffect(() => {
    refreshCSRFToken();
  }, [refreshCSRFToken]);
  
  return {
    csrfToken,
    isSecureContext,
    securityErrors,
    refreshCSRFToken,
  };
}

// Form validation hook with security
export function usePaymentFormValidation() {
  const [validationResult, setValidationResult] = useState<PaymentValidationResult>({
    isValid: true,
    errors: [],
    warnings: []
  });
  
  const [isValidating, setIsValidating] = useState(false);
  const debounceRef = useRef<NodeJS.Timeout>();
  
  const validateForm = useCallback((formData: Partial<CheckoutRequest>) => {
    // Debounce validation
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    
    debounceRef.current = setTimeout(() => {
      setIsValidating(true);
      
      try {
        // Only validate if we have required fields
        if (formData.amount && formData.itemName && formData.customerEmail) {
          const result = PaymentSecurityValidator.validateCheckoutRequest(formData as CheckoutRequest);
          setValidationResult(result);
        } else {
          setValidationResult({
            isValid: false,
            errors: ['Required fields missing'],
            warnings: []
          });
        }
      } catch (error) {
        setValidationResult({
          isValid: false,
          errors: [`Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`],
          warnings: []
        });
      } finally {
        setIsValidating(false);
      }
    }, 300);
  }, []);
  
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);
  
  return {
    validationResult,
    isValidating,
    validateForm,
  };
}

// Secure checkout hook
export function useSecureCheckout() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);
  const [checkoutData, setCheckoutData] = useState<any>(null);
  const { securityErrors, refreshCSRFToken } = usePaymentSecurity();
  
  const createCheckout = useCallback(async (request: CheckoutRequest) => {
    if (securityErrors.length > 0) {
      throw new Error(`Security validation failed: ${securityErrors.join(', ')}`);
    }
    
    setIsProcessing(true);
    setCheckoutError(null);
    
    try {
      const response = await paymentsApi.createCheckout(request);
      setCheckoutData(response);
      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Checkout failed';
      setCheckoutError(errorMessage);
      
      // Refresh CSRF token if it's a CSRF-related error
      if (errorMessage.includes('CSRF')) {
        await refreshCSRFToken();
      }
      
      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [securityErrors, refreshCSRFToken]);
  
  return {
    isProcessing,
    checkoutError,
    checkoutData,
    createCheckout,
  };
}

// Form input sanitization hook
export function useSecureFormInput(initialValue: string = '') {
  const [value, setValue] = useState(initialValue);
  const [sanitizedValue, setSanitizedValue] = useState(initialValue);
  const [hasSecurityIssues, setHasSecurityIssues] = useState(false);
  
  const sanitizeInput = useCallback((input: string): string => {
    // Remove potential XSS patterns
    let sanitized = input
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove script tags
      .replace(/javascript:/gi, '') // Remove javascript: protocols
      .replace(/data:/gi, '') // Remove data: protocols
      .replace(/vbscript:/gi, '') // Remove vbscript: protocols
      .replace(/on\w+\s*=/gi, '') // Remove event handlers
      .trim();
    
    // Additional sanitization for payment forms
    sanitized = sanitized.replace(/[<>]/g, ''); // Remove angle brackets
    
    return sanitized;
  }, []);
  
  const updateValue = useCallback((newValue: string) => {
    setValue(newValue);
    
    const sanitized = sanitizeInput(newValue);
    setSanitizedValue(sanitized);
    
    // Check if sanitization changed the value
    setHasSecurityIssues(newValue !== sanitized);
  }, [sanitizeInput]);
  
  return {
    value,
    sanitizedValue,
    hasSecurityIssues,
    updateValue,
  };
}

// Amount formatting and validation hook
export function usePaymentAmount(initialAmount: number = 0) {
  const [amount, setAmount] = useState(initialAmount);
  const [formattedAmount, setFormattedAmount] = useState('');
  const [amountError, setAmountError] = useState<string | null>(null);
  
  const formatAmount = useCallback((value: number): string => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  }, []);
  
  const updateAmount = useCallback((newAmount: string | number) => {
    const numAmount = typeof newAmount === 'string' ? parseFloat(newAmount) : newAmount;
    
    if (isNaN(numAmount)) {
      setAmountError('Invalid amount');
      return;
    }
    
    // Validate amount using security validator
    const validation = PaymentSecurityValidator.validateAmount(numAmount);
    
    if (!validation.isValid) {
      setAmountError(validation.errors.join(', '));
    } else {
      setAmountError(null);
    }
    
    setAmount(numAmount);
    setFormattedAmount(formatAmount(numAmount));
  }, [formatAmount]);
  
  useEffect(() => {
    updateAmount(initialAmount);
  }, [initialAmount, updateAmount]);
  
  return {
    amount,
    formattedAmount,
    amountError,
    updateAmount,
  };
}

// Rate limiting hook for payment operations
export function usePaymentRateLimit() {
  const [attemptCount, setAttemptCount] = useState(0);
  const [isBlocked, setIsBlocked] = useState(false);
  const [blockTimeRemaining, setBlockTimeRemaining] = useState(0);
  
  const MAX_ATTEMPTS = 5;
  const BLOCK_DURATION = 15 * 60 * 1000; // 15 minutes
  
  useEffect(() => {
    if (isBlocked && blockTimeRemaining > 0) {
      const timer = setInterval(() => {
        setBlockTimeRemaining(prev => {
          if (prev <= 1000) {
            setIsBlocked(false);
            setAttemptCount(0);
            return 0;
          }
          return prev - 1000;
        });
      }, 1000);
      
      return () => clearInterval(timer);
    }
  }, [isBlocked, blockTimeRemaining]);
  
  const recordAttempt = useCallback((wasSuccessful: boolean) => {
    if (wasSuccessful) {
      setAttemptCount(0);
      setIsBlocked(false);
      setBlockTimeRemaining(0);
    } else {
      setAttemptCount(prev => {
        const newCount = prev + 1;
        if (newCount >= MAX_ATTEMPTS) {
          setIsBlocked(true);
          setBlockTimeRemaining(BLOCK_DURATION);
        }
        return newCount;
      });
    }
  }, []);
  
  return {
    attemptCount,
    isBlocked,
    blockTimeRemaining: Math.ceil(blockTimeRemaining / 1000), // Convert to seconds
    recordAttempt,
    maxAttempts: MAX_ATTEMPTS,
  };
}

export {
  PaymentSecurityValidator,
  CSRFTokenManager
};