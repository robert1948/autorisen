/**
 * PayFast Payment API Service with Security Layer
 * Handles PayFast integration with comprehensive security validations
 */

import { apiRequest } from "../lib/api";

// Enhanced payment types with security metadata
export interface PaymentSecurityContext {
  csrfToken: string;
  sessionId?: string;
  timestamp: number;
  ipAddress?: string;
}

export interface PaymentMethod {
  id: string;
  userId: string;
  provider: 'payfast';
  methodType: 'card' | 'eft' | 'instant_eft' | 'bank_transfer';
  isDefault: boolean;
  isActive: boolean;
  providerToken: string;
  lastFour?: string;
  cardBrand?: string;
  expiryMonth?: number;
  expiryYear?: number;
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface Invoice {
  id: string;
  userId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'cancelled' | 'failed' | 'refunded';
  itemName: string;
  itemDescription?: string;
  customerEmail: string;
  customerFirstName: string;
  customerLastName: string;
  paymentProvider: string;
  externalReference: string;
  metadataJson?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface Transaction {
  id: string;
  invoiceId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'cancelled' | 'refunded';
  transactionType: 'payment' | 'refund' | 'chargeback';
  paymentProvider: string;
  providerTransactionId?: string;
  providerReference?: string;
  processedAt?: string;
  metadataJson?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface CheckoutRequest {
  amount: number;
  itemName: string;
  itemDescription?: string;
  customerEmail: string;
  customerFirstName: string;
  customerLastName: string;
  metadata?: Record<string, unknown>;
}

export interface PayFastCheckoutResponse {
  merchantId: string;
  merchantKey: string;
  processUrl: string;
  fields: Record<string, string>;
  signature: string;
}

export interface PaymentValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

// Security validation utilities
class PaymentSecurityValidator {
  private static readonly MIN_AMOUNT = 5.00; // Minimum ZAR 5
  private static readonly MAX_AMOUNT = 50000.00; // Maximum ZAR 50,000
  private static readonly ALLOWED_CURRENCIES = ['ZAR'];
  
  /**
   * Validate payment amount for security constraints
   */
  static validateAmount(amount: number): PaymentValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    if (amount < this.MIN_AMOUNT) {
      errors.push(`Amount must be at least ZAR ${this.MIN_AMOUNT}`);
    }
    
    if (amount > this.MAX_AMOUNT) {
      errors.push(`Amount exceeds maximum limit of ZAR ${this.MAX_AMOUNT}`);
    }
    
    if (!Number.isFinite(amount) || amount <= 0) {
      errors.push('Amount must be a positive number');
    }
    
    // Check for suspicious patterns
    const amountStr = amount.toString();
    if (amountStr.includes('e') || amountStr.includes('E')) {
      errors.push('Scientific notation not allowed in amount');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  /**
   * Validate customer data for security constraints
   */
  static validateCustomerData(request: CheckoutRequest): PaymentValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(request.customerEmail)) {
      errors.push('Invalid email address format');
    }
    
    // Name validation (prevent script injection)
    const nameRegex = /^[a-zA-Z\s'-]{1,64}$/;
    if (request.customerFirstName && !nameRegex.test(request.customerFirstName)) {
      errors.push('First name contains invalid characters');
    }
    
    if (request.customerLastName && !nameRegex.test(request.customerLastName)) {
      errors.push('Last name contains invalid characters');
    }
    
    // Item name validation
    if (!request.itemName || request.itemName.trim().length < 3) {
      errors.push('Item name must be at least 3 characters');
    }
    
    if (request.itemName.length > 100) {
      errors.push('Item name too long (max 100 characters)');
    }
    
    // Check for potential XSS patterns
    const xssPatterns = [/<script|javascript:|data:|vbscript:/i];
    const fieldsToCheck = [
      request.itemName,
      request.itemDescription || '',
      request.customerEmail,
      request.customerFirstName || '',
      request.customerLastName || ''
    ];
    
    for (const field of fieldsToCheck) {
      for (const pattern of xssPatterns) {
        if (pattern.test(field)) {
          errors.push('Invalid characters detected in form data');
          break;
        }
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
  
  /**
   * Comprehensive request validation
   */
  static validateCheckoutRequest(request: CheckoutRequest): PaymentValidationResult {
    const amountValidation = this.validateAmount(request.amount);
    const customerValidation = this.validateCustomerData(request);
    
    return {
      isValid: amountValidation.isValid && customerValidation.isValid,
      errors: [...amountValidation.errors, ...customerValidation.errors],
      warnings: [...amountValidation.warnings, ...customerValidation.warnings]
    };
  }
}

/**
 * Secure CSRF token management
 */
class CSRFTokenManager {
  private static token: string | null = null;
  private static expiry: number = 0;
  private static readonly TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes
  
  /**
   * Get current CSRF token, refresh if needed
   */
  static async getToken(): Promise<string> {
    const now = Date.now();
    
    // Check if token exists and is still valid
    if (this.token && now < this.expiry - this.TOKEN_REFRESH_THRESHOLD) {
      return this.token;
    }
    
    try {
      const response = await apiRequest<{ csrf_token: string }>('/auth/csrf', {
        method: 'GET',
        auth: false // CSRF endpoint doesn't require auth
      });
      
      this.token = response.csrf_token;
      this.expiry = now + (30 * 60 * 1000); // Token valid for 30 minutes
      
      return this.token;
    } catch (error) {
      throw new Error(`Failed to obtain CSRF token: ${error}`);
    }
  }
  
  /**
   * Clear cached token (force refresh on next request)
   */
  static clearToken(): void {
    this.token = null;
    this.expiry = 0;
  }
}

/**
 * Enhanced API request with payment security
 */
async function securePaymentRequest<T>(
  endpoint: string,
  options: {
    method?: string;
    body?: unknown;
    requireCSRF?: boolean;
  } = {}
): Promise<T> {
  const { method = 'GET', body, requireCSRF = true } = options;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  // Add CSRF protection for state-changing operations
  if (requireCSRF && method !== 'GET') {
    try {
      const csrfToken = await CSRFTokenManager.getToken();
      headers['X-CSRF-Token'] = csrfToken;
    } catch (error) {
      throw new Error(`CSRF protection failed: ${error}`);
    }
  }
  
  // Add security context
  headers['X-Payment-Context'] = JSON.stringify({
    timestamp: Date.now(),
    userAgent: navigator.userAgent.substring(0, 100), // Truncate for security
  });
  
  return apiRequest<T>(endpoint, {
    method,
    body,
    headers,
  });
}

/**
 * Payment API with comprehensive security
 */
export const paymentsApi = {
  /**
   * Create secure PayFast checkout session
   */
  async createCheckout(request: CheckoutRequest): Promise<PayFastCheckoutResponse> {
    // Pre-validate request
    const validation = PaymentSecurityValidator.validateCheckoutRequest(request);
    if (!validation.isValid) {
      throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
    }
    
    try {
      return await securePaymentRequest<PayFastCheckoutResponse>(
        '/payments/payfast/checkout',
        {
          method: 'POST',
          body: request,
          requireCSRF: true
        }
      );
    } catch (error) {
      // Clear CSRF token on certain errors to force refresh
      if (error instanceof Error && error.message.includes('CSRF')) {
        CSRFTokenManager.clearToken();
      }
      throw error;
    }
  },
  
  /**
   * List payment methods with security filtering
   */
  async listPaymentMethods(): Promise<PaymentMethod[]> {
    return securePaymentRequest<PaymentMethod[]>('/payments/methods');
  },
  
  /**
   * List invoices with pagination and security
   */
  async listInvoices(params?: { 
    limit?: number; 
    offset?: number; 
    status?: string;
  }): Promise<Invoice[]> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', String(Math.min(params.limit, 100))); // Cap at 100
    if (params?.offset) query.set('offset', String(Math.max(params.offset, 0)));
    if (params?.status) query.set('status', params.status);
    
    const endpoint = `/payments/invoices${query.toString() ? `?${query.toString()}` : ''}`;
    return securePaymentRequest<Invoice[]>(endpoint);
  },
  
  /**
   * Get single invoice with security validation
   */
  async getInvoice(invoiceId: string): Promise<Invoice> {
    // Validate invoice ID format (UUID)
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(invoiceId)) {
      throw new Error('Invalid invoice ID format');
    }
    
    return securePaymentRequest<Invoice>(`/payments/invoices/${invoiceId}`);
  },
  
  /**
   * List transactions for invoice
   */
  async listTransactions(invoiceId: string): Promise<Transaction[]> {
    // Validate invoice ID format
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(invoiceId)) {
      throw new Error('Invalid invoice ID format');
    }
    
    return securePaymentRequest<Transaction[]>(`/payments/invoices/${invoiceId}/transactions`);
  },
  
  /**
   * Cancel pending invoice
   */
  async cancelInvoice(invoiceId: string): Promise<{ status: string }> {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(invoiceId)) {
      throw new Error('Invalid invoice ID format');
    }
    
    return securePaymentRequest<{ status: string }>(
      `/payments/invoices/${invoiceId}/cancel`,
      {
        method: 'POST',
        requireCSRF: true
      }
    );
  }
};

// Export security utilities for component use
export { PaymentSecurityValidator, CSRFTokenManager };