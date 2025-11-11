/**
 * Payment Security Provider
 * Context provider for payment security state and validation
 */

import React, { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { CSRFTokenManager } from '../../services/paymentsApi';
import type { SecurityEvent, RateLimitInfo } from '../../types/payments';

interface PaymentSecurityContextType {
  // Security state
  isSecureContext: boolean;
  csrfToken: string | null;
  securityEvents: SecurityEvent[];
  
  // Rate limiting
  rateLimitInfo: RateLimitInfo;
  
  // Methods
  refreshCSRFToken: () => Promise<void>;
  recordSecurityEvent: (event: Omit<SecurityEvent, 'timestamp'>) => void;
  recordPaymentAttempt: (successful: boolean) => void;
  clearSecurityEvents: () => void;
}

const PaymentSecurityContext = createContext<PaymentSecurityContextType | null>(null);

interface PaymentSecurityProviderProps {
  children: ReactNode;
  maxAttempts?: number;
  blockDuration?: number;
}

export function PaymentSecurityProvider({ 
  children, 
  maxAttempts = 5,
  blockDuration = 15 * 60 * 1000 // 15 minutes
}: PaymentSecurityProviderProps) {
  const [isSecureContext, setIsSecureContext] = useState(false);
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [rateLimitInfo, setRateLimitInfo] = useState<RateLimitInfo>({
    attempts: 0,
    maxAttempts,
    isBlocked: false,
  });
  
  // Check secure context on mount
  useEffect(() => {
    const isSecure = window.location.protocol === 'https:' || 
                    window.location.hostname === 'localhost' ||
                    window.location.hostname === '127.0.0.1';
    setIsSecureContext(isSecure);
    
    if (!isSecure) {
      recordSecurityEvent({
        type: 'validation_error',
        message: 'Payment forms require HTTPS connection',
        context: { protocol: window.location.protocol }
      });
    }
  }, []);
  
  // Initialize CSRF token
  const refreshCSRFToken = useCallback(async () => {
    try {
      const token = await CSRFTokenManager.getToken();
      setCsrfToken(token);
      
      // Clear CSRF-related security events
      setSecurityEvents(prev => 
        prev.filter(event => event.type !== 'csrf_error')
      );
    } catch (error) {
      recordSecurityEvent({
        type: 'csrf_error',
        message: `Failed to obtain CSRF token: ${error instanceof Error ? error.message : 'Unknown error'}`,
        context: { error: String(error) }
      });
    }
  }, []);
  
  // Record security events
  const recordSecurityEvent = useCallback((event: Omit<SecurityEvent, 'timestamp'>) => {
    const securityEvent: SecurityEvent = {
      ...event,
      timestamp: Date.now(),
    };
    
    setSecurityEvents(prev => [...prev.slice(-19), securityEvent]); // Keep last 20 events
    
    // Log security events to console in development
    if (process.env.NODE_ENV === 'development') {
      console.warn('Payment Security Event:', securityEvent);
    }
  }, []);
  
  // Rate limiting logic
  const recordPaymentAttempt = useCallback((successful: boolean) => {
    if (successful) {
      // Reset on success
      setRateLimitInfo({
        attempts: 0,
        maxAttempts,
        isBlocked: false,
        resetTime: undefined,
      });
    } else {
      setRateLimitInfo((prev: RateLimitInfo) => {
        const newAttempts = prev.attempts + 1;
        const willBeBlocked = newAttempts >= maxAttempts;
        
        if (willBeBlocked) {
          const resetTime = Date.now() + blockDuration;
          
          recordSecurityEvent({
            type: 'rate_limit',
            message: `Payment attempts blocked after ${newAttempts} failed attempts`,
            context: {
              attempts: newAttempts,
              maxAttempts,
              resetTime,
              blockDuration,
            }
          });
          
          // Set timer to unblock
          setTimeout(() => {
            setRateLimitInfo((current: RateLimitInfo) => ({
              ...current,
              attempts: 0,
              isBlocked: false,
              resetTime: undefined,
            }));
          }, blockDuration);
          
          return {
            attempts: newAttempts,
            maxAttempts,
            isBlocked: true,
            resetTime,
          };
        }
        
        return {
          ...prev,
          attempts: newAttempts,
        };
      });
    }
  }, [maxAttempts, blockDuration, recordSecurityEvent]);
  
  const clearSecurityEvents = useCallback(() => {
    setSecurityEvents([]);
  }, []);
  
  // Initialize CSRF token on mount
  useEffect(() => {
    refreshCSRFToken();
  }, [refreshCSRFToken]);
  
  const contextValue: PaymentSecurityContextType = {
    isSecureContext,
    csrfToken,
    securityEvents,
    rateLimitInfo,
    refreshCSRFToken,
    recordSecurityEvent,
    recordPaymentAttempt,
    clearSecurityEvents,
  };
  
  return (
    <PaymentSecurityContext.Provider value={contextValue}>
      {children}
    </PaymentSecurityContext.Provider>
  );
}

// Hook to use payment security context
export function usePaymentSecurity() {
  const context = useContext(PaymentSecurityContext);
  if (!context) {
    throw new Error('usePaymentSecurity must be used within PaymentSecurityProvider');
  }
  return context;
}

// Security guard component
interface PaymentSecurityGuardProps {
  children: ReactNode;
  fallback?: ReactNode;
  requireSecureContext?: boolean;
  requireCSRFToken?: boolean;
}

export function PaymentSecurityGuard({
  children,
  fallback,
  requireSecureContext = true,
  requireCSRFToken = true,
}: PaymentSecurityGuardProps) {
  const { isSecureContext, csrfToken, securityEvents } = usePaymentSecurity();
  
  // Check security requirements
  const securityIssues: string[] = [];
  
  if (requireSecureContext && !isSecureContext) {
    securityIssues.push('Secure HTTPS connection required');
  }
  
  if (requireCSRFToken && !csrfToken) {
    securityIssues.push('Security token not available');
  }
  
  // Check for active security events
  const recentEvents = securityEvents.filter(
    event => Date.now() - event.timestamp < 60000 // Last minute
  );
  
  if (recentEvents.length > 0) {
    securityIssues.push(`Active security issues: ${recentEvents.length}`);
  }
  
  // Render fallback if security requirements not met
  if (securityIssues.length > 0) {
    if (fallback) {
      return <>{fallback}</>;
    }
    
    return (
      <div className="payment-security-warning">
        <div className="alert alert-warning">
          <h4>Security Requirements Not Met</h4>
          <ul>
            {securityIssues.map((issue, index) => (
              <li key={index}>{issue}</li>
            ))}
          </ul>
          <p>Payment functionality is temporarily disabled for security reasons.</p>
        </div>
      </div>
    );
  }
  
  return <>{children}</>;
}

// Security event display component
export function SecurityEventList() {
  const { securityEvents, clearSecurityEvents } = usePaymentSecurity();
  
  if (securityEvents.length === 0) {
    return null;
  }
  
  return (
    <div className="security-events">
      <div className="security-events__header">
        <h4>Security Events</h4>
        <button 
          type="button"
          onClick={clearSecurityEvents}
          className="btn btn-sm btn-outline-secondary"
        >
          Clear
        </button>
      </div>
      <div className="security-events__list">
        {securityEvents.slice(-5).map((event, index) => (
          <div 
            key={index}
            className={`security-event security-event--${event.type}`}
          >
            <div className="security-event__header">
              <span className="security-event__type">{event.type}</span>
              <span className="security-event__timestamp">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="security-event__message">
              {event.message}
            </div>
            {event.context && (
              <details className="security-event__context">
                <summary>Details</summary>
                <pre>{JSON.stringify(event.context, null, 2)}</pre>
              </details>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Rate limit display component
export function RateLimitDisplay() {
  const { rateLimitInfo } = usePaymentSecurity();
  
  if (!rateLimitInfo.isBlocked && rateLimitInfo.attempts === 0) {
    return null;
  }
  
  const remainingAttempts = rateLimitInfo.maxAttempts - rateLimitInfo.attempts;
  const resetTimeRemaining = rateLimitInfo.resetTime ? 
    Math.max(0, rateLimitInfo.resetTime - Date.now()) : 0;
  
  return (
    <div className={`rate-limit-display ${rateLimitInfo.isBlocked ? 'rate-limit-display--blocked' : ''}`}>
      {rateLimitInfo.isBlocked ? (
        <div className="alert alert-danger">
          <strong>Payment attempts blocked</strong>
          <p>
            Too many failed attempts. Please wait {Math.ceil(resetTimeRemaining / 1000)} seconds 
            before trying again.
          </p>
        </div>
      ) : (
        <div className="alert alert-warning">
          <strong>Warning:</strong> {remainingAttempts} payment attempts remaining
        </div>
      )}
    </div>
  );
}