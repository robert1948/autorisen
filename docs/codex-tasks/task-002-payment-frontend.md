# Codex Task 002: Payment System Frontend Integration

**Owner**: Codex  
**Status**: Ready for Implementation  
**Priority**: P1  
**Estimated Effort**: 3-4 days  

## 🎯 **Objective**

Build comprehensive payment frontend components to integrate with the existing PayFast backend infrastructure (primary provider), with Stripe configuration preserved but deactivated for future use. Focus on PayFast checkout flows, ITN handling, payment method management, and invoice history.

## 📋 **Implementation Tasks**

### **Task 1: Payment UI Components**

**Files to Create:**
- `client/src/components/payments/CheckoutFlow.tsx`
- `client/src/components/payments/PaymentMethodManager.tsx`
- `client/src/components/payments/InvoiceHistory.tsx`
- `client/src/components/payments/PaymentStatus.tsx`
- `client/src/components/payments/PaymentForm.tsx`

**Requirements:**
- Responsive payment forms with validation
- Payment method selection and management
- Invoice display with PDF download
- Payment status tracking with real-time updates
- Secure form handling with CSRF protection

### **Task 2: Payment API Client**

**Files to Create:**
- `client/src/services/paymentsApi.ts`
- `client/src/hooks/usePayments.ts`
- `client/src/types/payments.ts`

**Requirements:**
- Complete API client for payment endpoints
- React hooks for payment operations
- TypeScript interfaces matching backend models
- Error handling and retry logic
- Payment security validation

### **Task 3: Payment Integration Points**

**Files to Modify:**
- `client/src/pages/Dashboard.tsx` (add payment section)
- `client/src/components/nav/TopNav.tsx` (add billing link)
- `client/src/Router.tsx` (add payment routes)

**Requirements:**
- Integrate payment UI into existing app structure
- Add payment-related navigation elements
- Create protected routes for payment pages
- Link payment features to user dashboard

### **Task 4: Security & Testing**

**Files to Create:**
- `client/src/components/payments/__tests__/CheckoutFlow.test.tsx`
- `client/src/components/payments/__tests__/PaymentMethodManager.test.tsx`
- `client/src/services/__tests__/paymentsApi.test.ts`

**Requirements:**
- Comprehensive test coverage for payment flows
- Security validation testing
- Mock PayFast integration for testing
- End-to-end payment workflow tests

## 🔧 **Technical Specifications**

### **Payment Types:**

```typescript
// client/src/types/payments.ts
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
  amount: string;
  itemName: string;
  itemDescription: string;
  returnUrl: string;
  cancelUrl: string;
  notifyUrl: string;
  mPaymentId: string;
  signature: string;
  actionUrl: string;
}
```

### **Payment API Client:**

```typescript
// client/src/services/paymentsApi.ts
import { api } from './api';
import type { CheckoutRequest, PayFastCheckoutResponse, Invoice, PaymentMethod, Transaction } from '../types/payments';

export const paymentsApi = {
  // Checkout operations
  createCheckout: async (request: CheckoutRequest): Promise<PayFastCheckoutResponse> => {
    const response = await api.post('/api/payments/payfast/checkout', request);
    return response.data;
  },

  // Payment methods
  listPaymentMethods: async (): Promise<PaymentMethod[]> => {
    const response = await api.get('/api/payments/methods');
    return response.data;
  },

  // Invoices
  listInvoices: async (params?: { limit?: number; offset?: number }): Promise<Invoice[]> => {
    const response = await api.get('/api/payments/invoices', { params });
    return response.data;
  },

  getInvoice: async (id: string): Promise<Invoice> => {
    const response = await api.get(`/api/payments/invoices/${id}`);
    return response.data;
  },

  // Transactions
  listTransactions: async (invoiceId?: string): Promise<Transaction[]> => {
    const params = invoiceId ? { invoiceId } : {};
    const response = await api.get('/api/payments/transactions', { params });
    return response.data;
  }
};
```

### **Component Specifications:**

**CheckoutFlow.tsx:**
- Multi-step checkout process
- Payment method selection
- Order summary and confirmation
- PayFast form submission
- Success/failure handling

**PaymentMethodManager.tsx:**
- List saved payment methods
- Add new payment methods
- Set default payment method
- Remove payment methods
- Security confirmations

**InvoiceHistory.tsx:**
- Paginated invoice list
- Invoice detail view
- Payment status indicators
- Download/print functionality
- Search and filtering

## 🧪 **Testing Requirements**

### **Frontend Tests:**

```bash
# Component testing
npm test -- --testPathPattern=payments

# Integration testing with MSW
npm test -- --testPathPattern=paymentsApi

# Security testing
npm run test:security
```

### **Backend Integration:**

```bash
# Test payment endpoints
curl -X POST http://localhost:8000/api/payments/payfast/checkout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "itemName": "CapeControl Subscription",
    "customerEmail": "test@example.com",
    "customerFirstName": "Test",
    "customerLastName": "User"
  }'
```

## 🔒 **Security Requirements**

### **Frontend Security:**
- CSRF token validation for all payment forms
- Input sanitization and validation
- Secure storage of payment references (no card data)
- HTTPS-only payment submissions
- Rate limiting for payment attempts

### **Backend Integration:**
- Validate PayFast signatures
- Implement idempotency for payment operations
- Audit logging for all payment events
- Error handling without exposing sensitive data

## 📊 **Success Criteria**

### **KPIs to Achieve:**
- [ ] Payment form completion rate > 95%
- [ ] Checkout flow abandonment < 10%
- [ ] Payment processing latency < 5 seconds
- [ ] Test coverage > 90% for payment components
- [ ] Zero security vulnerabilities in payment code

### **User Experience Goals:**
- [ ] Intuitive payment flow
- [ ] Clear payment status feedback
- [ ] Responsive design on all devices
- [ ] Accessible payment forms
- [ ] Offline payment status sync

## 🚀 **Implementation Commands**

```bash
# Setup development environment
cd client
npm install

# Add payment dependencies
npm install @hookform/resolvers yup
npm install -D @testing-library/user-event

# Create payment components structure
mkdir -p src/components/payments
mkdir -p src/components/payments/__tests__
mkdir -p src/services
mkdir -p src/hooks
mkdir -p src/types

# Development server
npm run dev

# Testing
npm test -- --testPathPattern=payments
npm run test:coverage

# Build validation
npm run build
npm run type-check

# Backend testing
cd ../backend
python -m pytest tests/test_payments.py -v

# Full integration test
cd ../
make docker-build
make docker-run
```

## 📁 **File Structure**

```
client/src/
├── components/payments/
│   ├── CheckoutFlow.tsx (create)
│   ├── PaymentMethodManager.tsx (create)
│   ├── InvoiceHistory.tsx (create)
│   ├── PaymentStatus.tsx (create)
│   ├── PaymentForm.tsx (create)
│   └── __tests__/
│       ├── CheckoutFlow.test.tsx (create)
│       ├── PaymentMethodManager.test.tsx (create)
│       └── PaymentForm.test.tsx (create)
├── services/
│   ├── paymentsApi.ts (create)
│   └── __tests__/
│       └── paymentsApi.test.ts (create)
├── hooks/
│   └── usePayments.ts (create)
├── types/
│   └── payments.ts (create)
└── pages/
    ├── Billing.tsx (create)
    └── Checkout.tsx (create)
```

## 🔄 **Dependencies**

**Upstream Complete:**
- ✅ PayFast backend integration
- ✅ Payment database migration
- ✅ ITN webhook endpoint
- ✅ Payment API routes and schemas

**Downstream Enables:**
- User dashboard payment section
- Subscription management features
- Payment analytics and reporting
- Advanced billing workflows

## 🎯 **Delivery Milestones**

### **Week 1: Core Components**
- [ ] Payment types and API client
- [ ] Basic checkout flow
- [ ] Payment form with validation

### **Week 2: Management Features**
- [ ] Payment method manager
- [ ] Invoice history display
- [ ] Payment status tracking

### **Week 3: Integration & Testing**
- [ ] Dashboard integration
- [ ] Comprehensive testing
- [ ] Security validation
- [ ] Performance optimization

This task is ready for Codex implementation with clear specifications, comprehensive requirements, and detailed success criteria.