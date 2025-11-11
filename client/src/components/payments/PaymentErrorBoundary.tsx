/**
 * Payment Error Boundary
 * Comprehensive error handling for payment components with fallback UI
 */

import React, { Component, ReactNode, ErrorInfo } from 'react';
import type { PaymentErrorBoundaryState } from '../../types/payments';

interface PaymentErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
}

export class PaymentErrorBoundary extends Component<
  PaymentErrorBoundaryProps,
  PaymentErrorBoundaryState
> {
  constructor(props: PaymentErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: undefined,
      errorInfo: undefined,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<PaymentErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Payment Error Boundary caught an error:', error);
      console.error('Error details:', errorInfo);
    }

    // Store error info
    this.setState({
      errorInfo: errorInfo.componentStack || undefined,
    });

    // Call onError prop if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Report to error tracking service in production
    if (process.env.NODE_ENV === 'production') {
      this.reportError(error, errorInfo);
    }
  }

  componentDidUpdate(prevProps: PaymentErrorBoundaryProps) {
    // Reset error state if props change (useful for retries)
    if (this.props.resetOnPropsChange && 
        this.state.hasError && 
        prevProps.children !== this.props.children) {
      this.setState({
        hasError: false,
        error: undefined,
        errorInfo: undefined,
      });
    }
  }

  private reportError(error: Error, errorInfo: ErrorInfo) {
    // Report to error tracking service (e.g., Sentry)
    try {
      const errorReport = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        paymentContext: 'payment_component_error',
      };
      
      // Send to error tracking service
      // This would integrate with Sentry or similar service
      console.error('Payment error report:', errorReport);
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <PaymentErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          onRetry={this.handleRetry}
          onReload={this.handleReload}
        />
      );
    }

    return this.props.children;
  }
}

// Default error fallback component
interface PaymentErrorFallbackProps {
  error?: Error;
  errorInfo?: string;
  onRetry: () => void;
  onReload: () => void;
}

function PaymentErrorFallback({ 
  error, 
  errorInfo, 
  onRetry, 
  onReload 
}: PaymentErrorFallbackProps) {
  const isPaymentError = error?.message?.toLowerCase().includes('payment') ||
                        error?.message?.toLowerCase().includes('checkout') ||
                        error?.message?.toLowerCase().includes('payfast');
  
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <div className="payment-error-boundary">
      <div className="payment-error-boundary__container">
        <div className="payment-error-boundary__content">
          {/* Error icon */}
          <div className="payment-error-boundary__icon">
            <svg 
              className="w-16 h-16 text-red-500" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" 
              />
            </svg>
          </div>

          {/* Error message */}
          <div className="payment-error-boundary__message">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {isPaymentError ? 'Payment System Error' : 'Something went wrong'}
            </h2>
            <p className="text-gray-600 mb-4">
              {isPaymentError 
                ? 'There was an issue with the payment system. Your payment information is safe.'
                : 'An unexpected error occurred. Please try again.'
              }
            </p>
          </div>

          {/* Error details in development */}
          {isDevelopment && error && (
            <details className="payment-error-boundary__details">
              <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                Error Details (Development)
              </summary>
              <div className="mt-2 p-3 bg-gray-100 rounded text-xs">
                <div className="mb-2">
                  <strong>Error:</strong> {error.message}
                </div>
                {error.stack && (
                  <div className="mb-2">
                    <strong>Stack:</strong>
                    <pre className="whitespace-pre-wrap text-xs">{error.stack}</pre>
                  </div>
                )}
                {errorInfo && (
                  <div>
                    <strong>Component Stack:</strong>
                    <pre className="whitespace-pre-wrap text-xs">{errorInfo}</pre>
                  </div>
                )}
              </div>
            </details>
          )}

          {/* Action buttons */}
          <div className="payment-error-boundary__actions">
            <button
              type="button"
              onClick={onRetry}
              className="btn btn-primary mr-3"
            >
              Try Again
            </button>
            <button
              type="button"
              onClick={onReload}
              className="btn btn-outline-secondary mr-3"
            >
              Reload Page
            </button>
            <button
              type="button"
              onClick={() => window.history.back()}
              className="btn btn-outline-secondary"
            >
              Go Back
            </button>
          </div>

          {/* Help text */}
          <div className="payment-error-boundary__help">
            <p className="text-sm text-gray-500">
              If this problem persists, please{' '}
              <a 
                href="/support" 
                className="text-blue-600 hover:text-blue-700"
              >
                contact support
              </a>
              {' '}for assistance.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// HOC for wrapping components with error boundary
export function withPaymentErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<PaymentErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <PaymentErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </PaymentErrorBoundary>
  );
  
  WrappedComponent.displayName = `withPaymentErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}

// Hook for error reporting from functional components
export function usePaymentErrorHandler() {
  const reportError = React.useCallback((error: Error, context?: Record<string, unknown>) => {
    if (process.env.NODE_ENV === 'development') {
      console.error('Payment error:', error, context);
    }
    
    // Report to error tracking service
    try {
      const errorReport = {
        message: error.message,
        stack: error.stack,
        context,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        paymentContext: 'functional_component_error',
      };
      
      console.error('Payment error report:', errorReport);
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  }, []);
  
  return { reportError };
}

// CSS classes (to be moved to actual CSS file)
export const paymentErrorBoundaryStyles = `
.payment-error-boundary {
  @apply min-h-screen bg-gray-50 flex items-center justify-center p-4;
}

.payment-error-boundary__container {
  @apply max-w-md w-full;
}

.payment-error-boundary__content {
  @apply bg-white rounded-lg shadow-lg p-6 text-center;
}

.payment-error-boundary__icon {
  @apply flex justify-center mb-4;
}

.payment-error-boundary__message {
  @apply mb-6;
}

.payment-error-boundary__details {
  @apply text-left mb-6;
}

.payment-error-boundary__actions {
  @apply mb-4;
}

.payment-error-boundary__help {
  @apply text-center;
}

.btn {
  @apply px-4 py-2 rounded font-medium transition-colors;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-outline-secondary {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}
`;