/**
 * Payment Type Definitions with Security Enhancements
 * Comprehensive TypeScript types for PayFast payment integration
 */

// Plan catalog types
export interface Plan {
  id: string;
  name: string;
  description: string;
  price_monthly_zar: string;
  price_yearly_zar: string;
  product_code_monthly: string | null;
  product_code_yearly: string | null;
  features: string[];
  is_default: boolean;
  is_enterprise: boolean;
}

export interface PlansResponse {
  plans: Plan[];
  currency: string;
}

// Subscription types
export interface Subscription {
  id: string;
  plan_id: string;
  plan_name: string;
  status: 'active' | 'cancelled' | 'past_due' | 'trialing' | 'pending';
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  cancelled_at: string | null;
  created_at: string | null;
}

// Core payment entities
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

// Request/Response types
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
  process_url: string;
  fields: Record<string, string>;
  /** Optional — present when returned by some endpoints */
  merchantId?: string;
  merchantKey?: string;
  signature?: string;
}

// Security and validation types
export interface PaymentValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface PaymentSecurityContext {
  csrfToken: string;
  sessionId?: string;
  timestamp: number;
  ipAddress?: string;
}

export interface PaymentFormData {
  amount: string;
  itemName: string;
  itemDescription: string;
  customerEmail: string;
  customerFirstName: string;
  customerLastName: string;
  agreeToTerms: boolean;
}

// Form validation state
export interface PaymentFormValidation {
  amount: {
    isValid: boolean;
    error?: string;
    touched: boolean;
  };
  itemName: {
    isValid: boolean;
    error?: string;
    touched: boolean;
  };
  customerEmail: {
    isValid: boolean;
    error?: string;
    touched: boolean;
  };
  customerFirstName: {
    isValid: boolean;
    error?: string;
    touched: boolean;
  };
  customerLastName: {
    isValid: boolean;
    error?: string;
    touched: boolean;
  };
  agreeToTerms: {
    isValid: boolean;
    error?: string;
    touched: boolean;
  };
}

// Payment flow states
export type PaymentFlowStep = 
  | 'details'
  | 'review' 
  | 'processing'
  | 'success'
  | 'error';

export interface PaymentFlowState {
  currentStep: PaymentFlowStep;
  formData: PaymentFormData;
  validation: PaymentFormValidation;
  checkoutData?: PayFastCheckoutResponse;
  error?: string;
  isProcessing: boolean;
}

// API response wrappers
export interface PaginatedResponse<T> {
  results: T[];
  total: number;
  limit: number;
  offset: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface APIError {
  detail: string;
  code?: string;
  field?: string;
  status: number;
}

// PayFast specific types
export interface PayFastFormFields {
  merchant_id: string;
  merchant_key: string;
  return_url: string;
  cancel_url: string;
  notify_url: string;
  name_first?: string;
  name_last?: string;
  email_address: string;
  m_payment_id?: string;
  amount: string;
  item_name: string;
  item_description?: string;
  custom_int1?: string;
  custom_int2?: string;
  custom_int3?: string;
  custom_int4?: string;
  custom_int5?: string;
  custom_str1?: string;
  custom_str2?: string;
  custom_str3?: string;
  custom_str4?: string;
  custom_str5?: string;
  email_confirmation?: string;
  confirmation_address?: string;
  signature: string;
}

// Payment method management
export interface PaymentMethodCreate {
  methodType: PaymentMethod['methodType'];
  isDefault?: boolean;
}

export interface PaymentMethodUpdate {
  isDefault?: boolean;
  isActive?: boolean;
}

// Invoice filtering and searching
export interface InvoiceFilters {
  status?: Invoice['status'][];
  dateFrom?: string;
  dateTo?: string;
  amountMin?: number;
  amountMax?: number;
  search?: string;
}

export interface InvoiceListParams {
  limit?: number;
  offset?: number;
  filters?: InvoiceFilters;
  sortBy?: 'createdAt' | 'amount' | 'status';
  sortOrder?: 'asc' | 'desc';
}

// Component prop types
export interface PaymentFormProps {
  onSubmit: (data: CheckoutRequest) => Promise<void>;
  onCancel?: () => void;
  initialData?: Partial<PaymentFormData>;
  disabled?: boolean;
  className?: string;
}

export interface PaymentMethodManagerProps {
  methods: PaymentMethod[];
  onAdd: () => void;
  onEdit: (method: PaymentMethod) => void;
  onDelete: (methodId: string) => void;
  onSetDefault: (methodId: string) => void;
  className?: string;
}

export interface InvoiceHistoryProps {
  invoices: Invoice[];
  onLoadMore?: () => void;
  onFilterChange?: (filters: InvoiceFilters) => void;
  onInvoiceClick?: (invoice: Invoice) => void;
  hasMore?: boolean;
  isLoading?: boolean;
  className?: string;
}

export interface PaymentStatusProps {
  status: Invoice['status'];
  amount?: number;
  currency?: string;
  transactionId?: string;
  createdAt?: string;
  className?: string;
}

// Checkout flow props
export interface CheckoutFlowProps {
  onComplete: (result: PayFastCheckoutResponse) => void;
  onCancel: () => void;
  initialData?: Partial<PaymentFormData>;
  className?: string;
}

// Security event types
export interface SecurityEvent {
  type: 'csrf_error' | 'validation_error' | 'rate_limit' | 'suspicious_activity';
  message: string;
  timestamp: number;
  context?: Record<string, unknown>;
}

// Audit trail types
export interface PaymentAuditEvent {
  id: string;
  userId: string;
  action: 'checkout_created' | 'payment_completed' | 'payment_failed' | 'invoice_viewed';
  resourceId: string;
  resourceType: 'invoice' | 'transaction' | 'payment_method';
  metadata: Record<string, unknown>;
  ipAddress?: string;
  userAgent?: string;
  createdAt: string;
}

// Rate limiting types
export interface RateLimitInfo {
  attempts: number;
  maxAttempts: number;
  resetTime?: number;
  isBlocked: boolean;
}

// Error boundary types
export interface PaymentErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: string;
}

// WebSocket payment status updates
export interface PaymentStatusUpdate {
  invoiceId: string;
  status: Invoice['status'];
  transactionId?: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

// Export commonly used type unions
export type PaymentProvider = 'payfast';
export type PaymentCurrency = 'ZAR';
export type PaymentStatus = Invoice['status'];
export type TransactionStatus = Transaction['status'];
export type PaymentMethodType = PaymentMethod['methodType'];

// Default values and constants
export const DEFAULT_CURRENCY: PaymentCurrency = 'ZAR';
export const SUPPORTED_CURRENCIES: PaymentCurrency[] = ['ZAR'];

export const PAYMENT_STATUSES: PaymentStatus[] = [
  'pending', 'paid', 'cancelled', 'failed', 'refunded'
];

export const TRANSACTION_STATUSES: TransactionStatus[] = [
  'pending', 'completed', 'failed', 'cancelled', 'refunded'
];

export const PAYMENT_METHOD_TYPES: PaymentMethodType[] = [
  'card', 'eft', 'instant_eft', 'bank_transfer'
];

// Validation constants
export const VALIDATION_RULES = {
  AMOUNT: {
    MIN: 5.00,
    MAX: 50000.00,
  },
  ITEM_NAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 100,
  },
  CUSTOMER_NAME: {
    MAX_LENGTH: 64,
    PATTERN: /^[a-zA-Z\s'-]{1,64}$/,
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
} as const;