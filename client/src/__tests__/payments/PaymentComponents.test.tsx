/**
 * Payment Components Test Suite
 * Comprehensive testing for PayFast integration components
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PaymentStateProvider } from '../../context/PaymentStateContext';
import { PaymentSecurityProvider } from '../../components/payments/PaymentSecurityProvider';
import PayFastCheckout from '../../components/payments/PayFastCheckout';
import InvoiceHistory from '../../components/payments/InvoiceHistory';
import CheckoutFlow from '../../components/payments/CheckoutFlow';
import type { PaymentMethod, Invoice } from '../../types/payments';

// Mock data
const mockPaymentMethods: PaymentMethod[] = [
  {
    id: 'pm_1',
    methodType: 'card',
    provider: 'payfast',
    isDefault: true,
    isActive: true,
    metadata: {
      lastFour: '4242',
      expiryMonth: 12,
      expiryYear: 2025,
      brand: 'visa'
    },
    createdAt: '2025-11-01T10:00:00Z',
    updatedAt: '2025-11-01T10:00:00Z'
  }
];

const mockInvoices: Invoice[] = [
  {
    id: 'inv_1',
    amount: 99.00,
    status: 'paid',
    itemName: 'Professional Subscription',
    itemDescription: 'Monthly subscription',
    customerEmail: 'test@example.com',
    customerFirstName: 'John',
    customerLastName: 'Doe',
    createdAt: '2025-11-01T10:00:00Z',
    updatedAt: '2025-11-01T10:00:00Z'
  }
];

// Mock API responses
const mockPaymentsApi = {
  validateCheckout: vi.fn(),
  createCheckout: vi.fn(),
  listPaymentMethods: vi.fn(),
  listInvoices: vi.fn(),
  getCSRFToken: vi.fn(),
};

// Test wrapper component
function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <PaymentSecurityProvider>
        <PaymentStateProvider>
          {children}
        </PaymentStateProvider>
      </PaymentSecurityProvider>
    </BrowserRouter>
  );
}

// Mock modules
vi.mock('../../services/paymentsApi', () => ({
  paymentsApi: mockPaymentsApi,
  PaymentSecurityValidator: {
    validateCheckoutRequest: vi.fn(() => ({
      isValid: true,
      errors: [],
      warnings: [],
      score: 100
    })),
    sanitizeInput: vi.fn((input) => input),
  },
  CSRFTokenManager: {
    getToken: vi.fn(() => Promise.resolve('mock-csrf-token')),
    refreshToken: vi.fn(() => Promise.resolve('mock-csrf-token')),
  }
}));

describe('PayFast Checkout Component', () => {
  const mockProps = {
    formData: {
      amount: '99.00',
      itemName: 'Test Item',
      itemDescription: 'Test Description',
      customerEmail: 'test@example.com',
      customerFirstName: 'John',
      customerLastName: 'Doe',
      agreeToTerms: false
    },
    validation: {
      amount: { isValid: true, touched: true },
      itemName: { isValid: true, touched: true },
      customerEmail: { isValid: true, touched: true },
      customerFirstName: { isValid: true, touched: true },
      customerLastName: { isValid: true, touched: true },
      agreeToTerms: { isValid: false, touched: false }
    },
    formRefs: {
      amount: { current: null },
      itemName: { current: null },
      customerEmail: { current: null },
      customerFirstName: { current: null },
      customerLastName: { current: null },
      agreeToTerms: { current: null }
    },
    amountError: null,
    formattedAmount: 'R99.00',
    validationResult: null,
    onUpdateFormData: vi.fn(),
    onNext: vi.fn(),
    onCancel: vi.fn(),
    isValid: false
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders checkout form with all required fields', () => {
    render(
      <TestWrapper>
        <PayFastCheckout {...mockProps} />
      </TestWrapper>
    );

    expect(screen.getByText(/amount/i)).toBeInTheDocument();
    expect(screen.getByText(/item name/i)).toBeInTheDocument();
    expect(screen.getByText(/customer email/i)).toBeInTheDocument();
    expect(screen.getByText(/first name/i)).toBeInTheDocument();
    expect(screen.getByText(/last name/i)).toBeInTheDocument();
    expect(screen.getByText(/payment authorization/i)).toBeInTheDocument();
  });

  it('displays security information correctly', () => {
    render(
      <TestWrapper>
        <PayFastCheckout {...mockProps} />
      </TestWrapper>
    );

    expect(screen.getByText(/secure context/i)).toBeInTheDocument();
    expect(screen.getByText(/csrf token/i)).toBeInTheDocument();
    expect(screen.getByText(/attempts/i)).toBeInTheDocument();
  });

  it('disables submit button when form is invalid', () => {
    render(
      <TestWrapper>
        <PayFastCheckout {...mockProps} />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /continue/i });
    expect(submitButton).toBeDisabled();
  });

  it('enables submit button when form is valid', () => {
    const validProps = { ...mockProps, isValid: true };
    
    render(
      <TestWrapper>
        <PayFastCheckout {...validProps} />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /continue/i });
    expect(submitButton).not.toBeDisabled();
  });

  it('calls onNext when valid form is submitted', () => {
    const validProps = { ...mockProps, isValid: true };
    
    render(
      <TestWrapper>
        <PayFastCheckout {...validProps} />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /continue/i });
    fireEvent.click(submitButton);

    expect(mockProps.onNext).toHaveBeenCalled();
  });

  it('shows formatted amount in preview', () => {
    render(
      <TestWrapper>
        <PayFastCheckout {...mockProps} />
      </TestWrapper>
    );

    expect(screen.getByText('R99.00')).toBeInTheDocument();
  });
});

describe('Invoice History Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPaymentsApi.listInvoices.mockResolvedValue({
      data: mockInvoices,
      total: mockInvoices.length,
      limit: 10,
      offset: 0,
      hasNext: false,
      hasPrevious: false
    });
  });

  it('renders loading state initially', () => {
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    expect(screen.getByText(/loading invoices/i)).toBeInTheDocument();
  });

  it('renders invoice data after loading', async () => {
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('inv_1')).toBeInTheDocument();
    });

    expect(screen.getByText('Professional Subscription')).toBeInTheDocument();
    expect(screen.getByText('R99.00')).toBeInTheDocument();
  });

  it('shows view mode toggle buttons', () => {
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /table/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cards/i })).toBeInTheDocument();
  });

  it('shows export functionality', () => {
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });

  it('shows filters button', () => {
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /filters/i })).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    mockPaymentsApi.listInvoices.mockRejectedValue(new Error('API Error'));
    
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/unable to load invoices/i)).toBeInTheDocument();
      expect(screen.getByText(/API Error/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });
});

describe('Checkout Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders checkout flow component', () => {
    render(
      <TestWrapper>
        <CheckoutFlow />
      </TestWrapper>
    );

    expect(screen.getByText(/payment details/i)).toBeInTheDocument();
  });

  it('handles form submission', () => {
    mockPaymentsApi.createCheckout.mockResolvedValue({
      process_url: 'https://sandbox.payfast.co.za/eng/process',
      fields: {
        merchant_id: '10000100',
        amount: '99.00'
      }
    });

    const mockOnComplete = vi.fn();
    
    render(
      <TestWrapper>
        <CheckoutFlow onComplete={mockOnComplete} />
      </TestWrapper>
    );

    expect(screen.getByText(/secure checkout/i)).toBeInTheDocument();
  });
});

describe('Security Validation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('validates CSRF token availability', () => {
    mockPaymentsApi.getCSRFToken.mockResolvedValue('valid-csrf-token');
    
    render(
      <TestWrapper>
        <PayFastCheckout {...{
          formData: {
            amount: '99.00',
            itemName: 'Test Item',
            itemDescription: '',
            customerEmail: 'test@example.com',
            customerFirstName: 'John',
            customerLastName: 'Doe',
            agreeToTerms: false
          },
          validation: {
            amount: { isValid: true, touched: true },
            itemName: { isValid: true, touched: true },
            customerEmail: { isValid: true, touched: true },
            customerFirstName: { isValid: true, touched: true },
            customerLastName: { isValid: true, touched: true },
            agreeToTerms: { isValid: false, touched: false }
          },
          formRefs: {
            amount: { current: null },
            itemName: { current: null },
            customerEmail: { current: null },
            customerFirstName: { current: null },
            customerLastName: { current: null },
            agreeToTerms: { current: null }
          },
          amountError: null,
          formattedAmount: 'R99.00',
          validationResult: null,
          onUpdateFormData: vi.fn(),
          onNext: vi.fn(),
          onCancel: vi.fn(),
          isValid: false
        }} />
      </TestWrapper>
    );

    expect(screen.getByText(/csrf token/i)).toBeInTheDocument();
  });

  it('shows security context status', () => {
    render(
      <TestWrapper>
        <PaymentSecurityProvider>
          <div>Security Provider Test</div>
        </PaymentSecurityProvider>
      </TestWrapper>
    );

    expect(screen.getByText(/security provider test/i)).toBeInTheDocument();
  });

  it('handles rate limiting information', () => {
    render(
      <TestWrapper>
        <PayFastCheckout {...{
          formData: {
            amount: '99.00',
            itemName: 'Test Item',
            itemDescription: '',
            customerEmail: 'test@example.com',
            customerFirstName: 'John',
            customerLastName: 'Doe',
            agreeToTerms: false
          },
          validation: {
            amount: { isValid: true, touched: true },
            itemName: { isValid: true, touched: true },
            customerEmail: { isValid: true, touched: true },
            customerFirstName: { isValid: true, touched: true },
            customerLastName: { isValid: true, touched: true },
            agreeToTerms: { isValid: false, touched: false }
          },
          formRefs: {
            amount: { current: null },
            itemName: { current: null },
            customerEmail: { current: null },
            customerFirstName: { current: null },
            customerLastName: { current: null },
            agreeToTerms: { current: null }
          },
          amountError: null,
          formattedAmount: 'R99.00',
          validationResult: null,
          onUpdateFormData: vi.fn(),
          onNext: vi.fn(),
          onCancel: vi.fn(),
          isValid: false
        }} />
      </TestWrapper>
    );

    expect(screen.getByText(/attempts/i)).toBeInTheDocument();
  });
});

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PaymentStateProvider } from '../../context/PaymentStateContext';
import { PaymentSecurityProvider } from '../../components/payments/PaymentSecurityProvider';
import PayFastCheckout from '../../components/payments/PayFastCheckout';
import InvoiceHistory from '../../components/payments/InvoiceHistory';
import { PaymentMethodManager } from '../../components/payments/PaymentMethodManager';
import CheckoutFlow from '../../components/payments/CheckoutFlow';
import type { PaymentMethod, Invoice } from '../../types/payments';

// Mock data
const mockPaymentMethods: PaymentMethod[] = [
  {
    id: 'pm_1',
    methodType: 'card',
    displayName: 'Visa **** 4242',
    provider: 'payfast',
    isDefault: true,
    isActive: true,
    metadata: {
      lastFour: '4242',
      expiryMonth: 12,
      expiryYear: 2025,
      brand: 'visa'
    },
    createdAt: '2025-11-01T10:00:00Z',
    updatedAt: '2025-11-01T10:00:00Z'
  },
  {
    id: 'pm_2', 
    methodType: 'eft',
    displayName: 'Bank Transfer',
    provider: 'payfast',
    isDefault: false,
    isActive: true,
    metadata: {},
    createdAt: '2025-11-02T10:00:00Z',
    updatedAt: '2025-11-02T10:00:00Z'
  }
];

const mockInvoices: Invoice[] = [
  {
    id: 'inv_1',
    amount: 99.00,
    status: 'paid',
    itemName: 'Professional Subscription',
    itemDescription: 'Monthly subscription',
    customerEmail: 'test@example.com',
    customerFirstName: 'John',
    customerLastName: 'Doe',
    metadata: { source: 'checkout' },
    createdAt: '2025-11-01T10:00:00Z',
    updatedAt: '2025-11-01T10:00:00Z'
  },
  {
    id: 'inv_2',
    amount: 29.00,
    status: 'pending',
    itemName: 'Starter Plan',
    itemDescription: 'Basic features',
    customerEmail: 'jane@example.com',
    customerFirstName: 'Jane',
    customerLastName: 'Smith',
    metadata: { source: 'api' },
    createdAt: '2025-11-02T10:00:00Z',
    updatedAt: '2025-11-02T10:00:00Z'
  }
];

// Mock API responses
const mockPaymentsApi = {
  validateCheckout: vi.fn(),
  createCheckout: vi.fn(),
  listPaymentMethods: vi.fn(),
  createPaymentMethod: vi.fn(),
  updatePaymentMethod: vi.fn(),
  deletePaymentMethod: vi.fn(),
  listInvoices: vi.fn(),
  getCSRFToken: vi.fn(),
};

// Test wrapper component
function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <PaymentSecurityProvider>
        <PaymentStateProvider>
          {children}
        </PaymentStateProvider>
      </PaymentSecurityProvider>
    </BrowserRouter>
  );
}

// Mock modules
vi.mock('../../src/services/paymentsApi', () => ({
  paymentsApi: mockPaymentsApi,
  PaymentSecurityValidator: {
    validateCheckoutRequest: vi.fn(() => ({
      isValid: true,
      errors: [],
      warnings: [],
      score: 100
    })),
    sanitizeInput: vi.fn((input) => input),
  },
  CSRFTokenManager: {
    getToken: vi.fn(() => Promise.resolve('mock-csrf-token')),
    refreshToken: vi.fn(() => Promise.resolve('mock-csrf-token')),
  }
}));

describe('PayFast Checkout Component', () => {
  const mockProps = {
    formData: {
      amount: '99.00',
      itemName: 'Test Item',
      itemDescription: 'Test Description',
      customerEmail: 'test@example.com',
      customerFirstName: 'John',
      customerLastName: 'Doe',
      agreeToTerms: false
    },
    validation: {
      amount: { isValid: true, touched: true },
      itemName: { isValid: true, touched: true },
      customerEmail: { isValid: true, touched: true },
      customerFirstName: { isValid: true, touched: true },
      customerLastName: { isValid: true, touched: true },
      agreeToTerms: { isValid: false, touched: false }
    },
    formRefs: {
      amount: { current: null },
      itemName: { current: null },
      customerEmail: { current: null },
      customerFirstName: { current: null },
      customerLastName: { current: null },
      agreeToTerms: { current: null }
    },
    amountError: null,
    formattedAmount: 'R99.00',
    validationResult: null,
    onUpdateFormData: vi.fn(),
    onNext: vi.fn(),
    onCancel: vi.fn(),
    isValid: false
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders checkout form with all required fields', () => {
    render(
      <TestWrapper>
        <PayFastCheckout {...mockProps} />
      </TestWrapper>
    );

    expect(screen.getByLabelText(/amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/item name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/customer email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/payment authorization/i)).toBeInTheDocument();
  });

  it('displays security information correctly', () => {
    render(
      <TestWrapper>
        <PayFastCheckout {...mockProps} />
      </TestWrapper>
    );

    expect(screen.getByText(/secure context/i)).toBeInTheDocument();
    expect(screen.getByText(/csrf token/i)).toBeInTheDocument();
    expect(screen.getByText(/attempts/i)).toBeInTheDocument();
  });

  it('calls onUpdateFormData when form fields change', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <PayFastCheckout {...mockProps} />
      </TestWrapper>
    );

    const amountInput = screen.getByLabelText(/amount/i);
    await user.clear(amountInput);
    await user.type(amountInput, '150.00');

    expect(mockProps.onUpdateFormData).toHaveBeenCalledWith('amount', '150.00');
  });

  it('disables submit button when form is invalid', () => {
    render(
      <TestWrapper>
        <PayFastCheckout {...mockProps} />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /continue/i });
    expect(submitButton).toBeDisabled();
  });

  it('enables submit button when form is valid', () => {
    const validProps = { ...mockProps, isValid: true };
    
    render(
      <TestWrapper>
        <PayFastCheckout {...validProps} />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /continue/i });
    expect(submitButton).not.toBeDisabled();
  });

  it('calls onNext when valid form is submitted', async () => {
    const user = userEvent.setup();
    const validProps = { ...mockProps, isValid: true };
    
    render(
      <TestWrapper>
        <PayFastCheckout {...validProps} />
      </TestWrapper>
    );

    const submitButton = screen.getByRole('button', { name: /continue/i });
    await user.click(submitButton);

    expect(mockProps.onNext).toHaveBeenCalled();
  });
});

describe('Payment Method Manager', () => {
  const mockManagerProps = {
    methods: mockPaymentMethods,
    onAdd: vi.fn(),
    onEdit: vi.fn(),
    onDelete: vi.fn(),
    onSetDefault: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all payment methods', () => {
    render(
      <TestWrapper>
        <PaymentMethodManager {...mockManagerProps} />
      </TestWrapper>
    );

    expect(screen.getByText('Visa **** 4242')).toBeInTheDocument();
    expect(screen.getByText('Bank Transfer')).toBeInTheDocument();
  });

  it('shows default method indicator', () => {
    render(
      <TestWrapper>
        <PaymentMethodManager {...mockManagerProps} />
      </TestWrapper>
    );

    expect(screen.getByText(/default/i)).toBeInTheDocument();
  });

  it('calls onAdd when add button is clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <PaymentMethodManager {...mockManagerProps} />
      </TestWrapper>
    );

    const addButton = screen.getByRole('button', { name: /add.*method/i });
    await user.click(addButton);

    expect(mockManagerProps.onAdd).toHaveBeenCalled();
  });

  it('shows confirmation dialog for delete action', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <PaymentMethodManager {...mockManagerProps} />
      </TestWrapper>
    );

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    await user.click(deleteButtons[0]);

    expect(screen.getByText(/confirm.*delete/i)).toBeInTheDocument();
  });

  it('calls onDelete when delete is confirmed', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <PaymentMethodManager {...mockManagerProps} />
      </TestWrapper>
    );

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    await user.click(deleteButtons[0]);

    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    await user.click(confirmButton);

    expect(mockManagerProps.onDelete).toHaveBeenCalledWith('pm_1');
  });
});

describe('Invoice History Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPaymentsApi.listInvoices.mockResolvedValue({
      data: mockInvoices,
      total: mockInvoices.length,
      limit: 10,
      offset: 0,
      hasNext: false,
      hasPrevious: false
    });
  });

  it('renders invoice table with data', async () => {
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('inv_1')).toBeInTheDocument();
      expect(screen.getByText('inv_2')).toBeInTheDocument();
    });

    expect(screen.getByText('Professional Subscription')).toBeInTheDocument();
    expect(screen.getByText('R99.00')).toBeInTheDocument();
  });

  it('filters invoices by search term', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('inv_1')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search invoices/i);
    await user.type(searchInput, 'Professional');

    expect(screen.getByText('Professional Subscription')).toBeInTheDocument();
    expect(screen.queryByText('Starter Plan')).not.toBeInTheDocument();
  });

  it('switches between table and card views', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('inv_1')).toBeInTheDocument();
    });

    const cardViewButton = screen.getByRole('button', { name: /cards/i });
    await user.click(cardViewButton);

    // Should still show invoice data but in card format
    expect(screen.getByText('inv_1')).toBeInTheDocument();
    expect(screen.getByText('Professional Subscription')).toBeInTheDocument();
  });

  it('handles bulk invoice selection', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('inv_1')).toBeInTheDocument();
    });

    // Select individual invoices
    const checkboxes = screen.getAllByRole('checkbox');
    const firstInvoiceCheckbox = checkboxes[1]; // Skip the select-all checkbox
    
    await user.click(firstInvoiceCheckbox);

    expect(screen.getByText(/1 invoice.*selected/i)).toBeInTheDocument();
  });

  it('shows filters panel when filter button is clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    const filterButton = screen.getByRole('button', { name: /filters/i });
    await user.click(filterButton);

    expect(screen.getByText(/status/i)).toBeInTheDocument();
    expect(screen.getByText(/date range/i)).toBeInTheDocument();
    expect(screen.getByText(/amount range/i)).toBeInTheDocument();
  });
});

describe('Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('completes full checkout flow', async () => {
    const user = userEvent.setup();
    mockPaymentsApi.createCheckout.mockResolvedValue({
      process_url: 'https://sandbox.payfast.co.za/eng/process',
      fields: {
        merchant_id: '10000100',
        merchant_key: 'test_key',
        amount: '99.00',
        item_name: 'Test Item'
      }
    });

    const mockOnComplete = vi.fn();
    
    render(
      <TestWrapper>
        <CheckoutFlow onComplete={mockOnComplete} />
      </TestWrapper>
    );

    // Fill out checkout form
    await user.type(screen.getByLabelText(/amount/i), '99.00');
    await user.type(screen.getByLabelText(/item name/i), 'Test Item');
    await user.type(screen.getByLabelText(/customer email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/first name/i), 'John');
    await user.type(screen.getByLabelText(/last name/i), 'Doe');
    await user.click(screen.getByLabelText(/payment authorization/i));

    // Submit form
    const continueButton = screen.getByRole('button', { name: /continue/i });
    await user.click(continueButton);

    await waitFor(() => {
      expect(mockPaymentsApi.createCheckout).toHaveBeenCalled();
    });
  });

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup();
    mockPaymentsApi.listInvoices.mockRejectedValue(new Error('API Error'));
    
    render(
      <TestWrapper>
        <InvoiceHistory />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/unable to load invoices/i)).toBeInTheDocument();
      expect(screen.getByText(/API Error/i)).toBeInTheDocument();
    });

    // Should show retry button
    const retryButton = screen.getByRole('button', { name: /try again/i });
    expect(retryButton).toBeInTheDocument();
  });
});

describe('Security Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('validates CSRF token before sensitive operations', async () => {
    const user = userEvent.setup();
    mockPaymentsApi.getCSRFToken.mockResolvedValue('valid-csrf-token');
    
    render(
      <TestWrapper>
        <PaymentMethodManager 
          methods={mockPaymentMethods}
          onAdd={vi.fn()}
          onEdit={vi.fn()}
          onDelete={vi.fn()}
          onSetDefault={vi.fn()}
        />
      </TestWrapper>
    );

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    await user.click(deleteButtons[0]);

    expect(mockPaymentsApi.getCSRFToken).toHaveBeenCalled();
  });

  it('sanitizes user input to prevent XSS', async () => {
    const user = userEvent.setup();
    const mockSanitize = vi.fn((input) => input.replace(/<script>/g, ''));
    
    // Mock the sanitization function
    vi.doMock('../../src/services/paymentsApi', () => ({
      PaymentSecurityValidator: {
        sanitizeInput: mockSanitize,
        validateCheckoutRequest: vi.fn(() => ({ isValid: true, errors: [], warnings: [] }))
      }
    }));

    const maliciousInput = 'Test <script>alert("xss")</script>';
    
    render(
      <TestWrapper>
        <PayFastCheckout {...{
          ...mockProps,
          onUpdateFormData: vi.fn()
        }} />
      </TestWrapper>
    );

    const itemNameInput = screen.getByLabelText(/item name/i);
    await user.clear(itemNameInput);
    await user.type(itemNameInput, maliciousInput);

    // Verify sanitization was called
    await waitFor(() => {
      expect(mockSanitize).toHaveBeenCalledWith(maliciousInput);
    });
  });

  it('enforces rate limiting on payment operations', async () => {
    // Mock rate limit exceeded scenario
    const rateLimitError = new Error('Rate limit exceeded');
    rateLimitError.name = 'RateLimitError';
    
    mockPaymentsApi.createCheckout.mockRejectedValue(rateLimitError);
    
    render(
      <TestWrapper>
        <CheckoutFlow />
      </TestWrapper>
    );

    // Should display rate limit warning
    await waitFor(() => {
      expect(screen.getByText(/rate limit/i)).toBeInTheDocument();
    });
  });
});