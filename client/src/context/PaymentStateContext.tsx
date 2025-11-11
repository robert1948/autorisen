/**
 * Payment State Management Context
 * Centralized state management for complex payment operations
 */

import React, { createContext, useContext, useReducer, useEffect, useCallback, ReactNode } from 'react';
import { paymentsApi } from '../services/paymentsApi';
import type { 
  PaymentMethod, 
  Invoice, 
  Transaction, 
  PayFastCheckoutResponse,
  InvoiceFilters,
  PaginatedResponse 
} from '../types/payments';

// State interface
interface PaymentState {
  // Payment methods
  paymentMethods: PaymentMethod[];
  paymentMethodsLoading: boolean;
  paymentMethodsError: string | null;
  
  // Invoices
  invoices: Invoice[];
  invoicesLoading: boolean;
  invoicesError: string | null;
  invoicesPagination: {
    total: number;
    limit: number;
    offset: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  invoiceFilters: InvoiceFilters;
  
  // Current checkout
  currentCheckout: PayFastCheckoutResponse | null;
  checkoutLoading: boolean;
  checkoutError: string | null;
  
  // Transaction history
  transactions: Record<string, Transaction[]>; // Keyed by invoice ID
  transactionsLoading: Record<string, boolean>;
  transactionsError: Record<string, string>;
  
  // UI state
  activeInvoiceId: string | null;
  isPaymentMethodModalOpen: boolean;
  isInvoiceDetailModalOpen: boolean;
}

// Action types
type PaymentAction =
  | { type: 'PAYMENT_METHODS_LOADING' }
  | { type: 'PAYMENT_METHODS_SUCCESS'; payload: PaymentMethod[] }
  | { type: 'PAYMENT_METHODS_ERROR'; payload: string }
  | { type: 'INVOICES_LOADING' }
  | { type: 'INVOICES_SUCCESS'; payload: PaginatedResponse<Invoice> }
  | { type: 'INVOICES_ERROR'; payload: string }
  | { type: 'INVOICES_APPEND'; payload: Invoice[] }
  | { type: 'INVOICE_FILTERS_UPDATE'; payload: Partial<InvoiceFilters> }
  | { type: 'CHECKOUT_LOADING' }
  | { type: 'CHECKOUT_SUCCESS'; payload: PayFastCheckoutResponse }
  | { type: 'CHECKOUT_ERROR'; payload: string }
  | { type: 'CHECKOUT_CLEAR' }
  | { type: 'TRANSACTIONS_LOADING'; payload: string }
  | { type: 'TRANSACTIONS_SUCCESS'; payload: { invoiceId: string; transactions: Transaction[] } }
  | { type: 'TRANSACTIONS_ERROR'; payload: { invoiceId: string; error: string } }
  | { type: 'SET_ACTIVE_INVOICE'; payload: string | null }
  | { type: 'SET_PAYMENT_METHOD_MODAL'; payload: boolean }
  | { type: 'SET_INVOICE_DETAIL_MODAL'; payload: boolean }
  | { type: 'PAYMENT_METHOD_ADDED'; payload: PaymentMethod }
  | { type: 'PAYMENT_METHOD_UPDATED'; payload: PaymentMethod }
  | { type: 'PAYMENT_METHOD_REMOVED'; payload: string }
  | { type: 'INVOICE_STATUS_UPDATE'; payload: { invoiceId: string; status: Invoice['status'] } };

// Initial state
const initialState: PaymentState = {
  paymentMethods: [],
  paymentMethodsLoading: false,
  paymentMethodsError: null,
  
  invoices: [],
  invoicesLoading: false,
  invoicesError: null,
  invoicesPagination: {
    total: 0,
    limit: 20,
    offset: 0,
    hasNext: false,
    hasPrevious: false,
  },
  invoiceFilters: {},
  
  currentCheckout: null,
  checkoutLoading: false,
  checkoutError: null,
  
  transactions: {},
  transactionsLoading: {},
  transactionsError: {},
  
  activeInvoiceId: null,
  isPaymentMethodModalOpen: false,
  isInvoiceDetailModalOpen: false,
};

// Reducer
function paymentReducer(state: PaymentState, action: PaymentAction): PaymentState {
  switch (action.type) {
    case 'PAYMENT_METHODS_LOADING':
      return { ...state, paymentMethodsLoading: true, paymentMethodsError: null };
      
    case 'PAYMENT_METHODS_SUCCESS':
      return { 
        ...state, 
        paymentMethods: action.payload, 
        paymentMethodsLoading: false, 
        paymentMethodsError: null 
      };
      
    case 'PAYMENT_METHODS_ERROR':
      return { 
        ...state, 
        paymentMethodsLoading: false, 
        paymentMethodsError: action.payload 
      };
      
    case 'INVOICES_LOADING':
      return { ...state, invoicesLoading: true, invoicesError: null };
      
    case 'INVOICES_SUCCESS':
      return {
        ...state,
        invoices: action.payload.results,
        invoicesLoading: false,
        invoicesError: null,
        invoicesPagination: {
          total: action.payload.total,
          limit: action.payload.limit,
          offset: action.payload.offset,
          hasNext: action.payload.hasNext,
          hasPrevious: action.payload.hasPrevious,
        }
      };
      
    case 'INVOICES_ERROR':
      return { ...state, invoicesLoading: false, invoicesError: action.payload };
      
    case 'INVOICES_APPEND':
      return {
        ...state,
        invoices: [...state.invoices, ...action.payload],
        invoicesLoading: false,
      };
      
    case 'INVOICE_FILTERS_UPDATE':
      return {
        ...state,
        invoiceFilters: { ...state.invoiceFilters, ...action.payload },
      };
      
    case 'CHECKOUT_LOADING':
      return { ...state, checkoutLoading: true, checkoutError: null };
      
    case 'CHECKOUT_SUCCESS':
      return { 
        ...state, 
        currentCheckout: action.payload, 
        checkoutLoading: false, 
        checkoutError: null 
      };
      
    case 'CHECKOUT_ERROR':
      return { 
        ...state, 
        checkoutLoading: false, 
        checkoutError: action.payload 
      };
      
    case 'CHECKOUT_CLEAR':
      return { 
        ...state, 
        currentCheckout: null, 
        checkoutError: null 
      };
      
    case 'TRANSACTIONS_LOADING':
      return {
        ...state,
        transactionsLoading: { ...state.transactionsLoading, [action.payload]: true },
        transactionsError: { ...state.transactionsError, [action.payload]: '' },
      };
      
    case 'TRANSACTIONS_SUCCESS':
      return {
        ...state,
        transactions: { ...state.transactions, [action.payload.invoiceId]: action.payload.transactions },
        transactionsLoading: { ...state.transactionsLoading, [action.payload.invoiceId]: false },
      };
      
    case 'TRANSACTIONS_ERROR':
      return {
        ...state,
        transactionsLoading: { ...state.transactionsLoading, [action.payload.invoiceId]: false },
        transactionsError: { ...state.transactionsError, [action.payload.invoiceId]: action.payload.error },
      };
      
    case 'SET_ACTIVE_INVOICE':
      return { ...state, activeInvoiceId: action.payload };
      
    case 'SET_PAYMENT_METHOD_MODAL':
      return { ...state, isPaymentMethodModalOpen: action.payload };
      
    case 'SET_INVOICE_DETAIL_MODAL':
      return { ...state, isInvoiceDetailModalOpen: action.payload };
      
    case 'PAYMENT_METHOD_ADDED':
      return {
        ...state,
        paymentMethods: [...state.paymentMethods, action.payload],
      };
      
    case 'PAYMENT_METHOD_UPDATED':
      return {
        ...state,
        paymentMethods: state.paymentMethods.map(method =>
          method.id === action.payload.id ? action.payload : method
        ),
      };
      
    case 'PAYMENT_METHOD_REMOVED':
      return {
        ...state,
        paymentMethods: state.paymentMethods.filter(method => method.id !== action.payload),
      };
      
    case 'INVOICE_STATUS_UPDATE':
      return {
        ...state,
        invoices: state.invoices.map(invoice =>
          invoice.id === action.payload.invoiceId 
            ? { ...invoice, status: action.payload.status }
            : invoice
        ),
      };
      
    default:
      return state;
  }
}

// Context
const PaymentStateContext = createContext<{
  state: PaymentState;
  dispatch: React.Dispatch<PaymentAction>;
} | null>(null);

// Context provider
export function PaymentStateProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(paymentReducer, initialState);
  
  return (
    <PaymentStateContext.Provider value={{ state, dispatch }}>
      {children}
    </PaymentStateContext.Provider>
  );
}

// Hook for using payment state
export function usePaymentState() {
  const context = useContext(PaymentStateContext);
  if (!context) {
    throw new Error('usePaymentState must be used within PaymentStateProvider');
  }
  return context;
}

// High-level hooks for specific operations
export function usePaymentMethods() {
  const { state, dispatch } = usePaymentState();
  
  const loadPaymentMethods = useCallback(async () => {
    if (state.paymentMethodsLoading) return;
    
    dispatch({ type: 'PAYMENT_METHODS_LOADING' });
    try {
      const methods = await paymentsApi.listPaymentMethods();
      dispatch({ type: 'PAYMENT_METHODS_SUCCESS', payload: methods });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load payment methods';
      dispatch({ type: 'PAYMENT_METHODS_ERROR', payload: message });
    }
  }, [state.paymentMethodsLoading, dispatch]);
  
  const addPaymentMethod = useCallback((method: PaymentMethod) => {
    dispatch({ type: 'PAYMENT_METHOD_ADDED', payload: method });
  }, [dispatch]);
  
  const updatePaymentMethod = useCallback((method: PaymentMethod) => {
    dispatch({ type: 'PAYMENT_METHOD_UPDATED', payload: method });
  }, [dispatch]);
  
  const removePaymentMethod = useCallback((methodId: string) => {
    dispatch({ type: 'PAYMENT_METHOD_REMOVED', payload: methodId });
  }, [dispatch]);
  
  return {
    paymentMethods: state.paymentMethods,
    loading: state.paymentMethodsLoading,
    error: state.paymentMethodsError,
    loadPaymentMethods,
    addPaymentMethod,
    updatePaymentMethod,
    removePaymentMethod,
  };
}

export function useInvoices() {
  const { state, dispatch } = usePaymentState();
  
  const loadInvoices = useCallback(async (params?: {
    limit?: number;
    offset?: number;
    filters?: InvoiceFilters;
    append?: boolean;
  }) => {
    if (state.invoicesLoading) return;
    
    dispatch({ type: 'INVOICES_LOADING' });
    try {
      const invoiceParams = {
        limit: params?.limit || state.invoicesPagination.limit,
        offset: params?.offset || 0,
        filters: params?.filters || state.invoiceFilters,
      };
      
      // Convert filters to API params
      const apiParams: any = {
        limit: invoiceParams.limit,
        offset: invoiceParams.offset,
      };
      
      if (invoiceParams.filters.status && invoiceParams.filters.status.length > 0) {
        apiParams.status = invoiceParams.filters.status.join(',');
      }
      
      const invoices = await paymentsApi.listInvoices(apiParams);
      
      // Mock pagination response (backend should provide this)
      const paginatedResponse = {
        results: invoices,
        total: invoices.length, // Backend should provide actual total
        limit: invoiceParams.limit,
        offset: invoiceParams.offset,
        hasNext: false, // Backend should calculate this
        hasPrevious: invoiceParams.offset > 0,
      };
      
      if (params?.append) {
        dispatch({ type: 'INVOICES_APPEND', payload: invoices });
      } else {
        dispatch({ type: 'INVOICES_SUCCESS', payload: paginatedResponse });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load invoices';
      dispatch({ type: 'INVOICES_ERROR', payload: message });
    }
  }, [state.invoicesLoading, state.invoicesPagination.limit, state.invoiceFilters, dispatch]);
  
  const updateInvoiceFilters = useCallback((filters: Partial<InvoiceFilters>) => {
    dispatch({ type: 'INVOICE_FILTERS_UPDATE', payload: filters });
  }, [dispatch]);
  
  const loadMoreInvoices = useCallback(() => {
    const newOffset = state.invoices.length;
    loadInvoices({ 
      offset: newOffset, 
      append: true 
    });
  }, [state.invoices.length, loadInvoices]);
  
  return {
    invoices: state.invoices,
    loading: state.invoicesLoading,
    error: state.invoicesError,
    pagination: state.invoicesPagination,
    filters: state.invoiceFilters,
    loadInvoices,
    loadMoreInvoices,
    updateInvoiceFilters,
  };
}

export function useTransactions() {
  const { state, dispatch } = usePaymentState();
  
  const loadTransactions = useCallback(async (invoiceId: string) => {
    if (state.transactionsLoading[invoiceId]) return;
    
    dispatch({ type: 'TRANSACTIONS_LOADING', payload: invoiceId });
    try {
      const transactions = await paymentsApi.listTransactions(invoiceId);
      dispatch({ 
        type: 'TRANSACTIONS_SUCCESS', 
        payload: { invoiceId, transactions } 
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load transactions';
      dispatch({ 
        type: 'TRANSACTIONS_ERROR', 
        payload: { invoiceId, error: message } 
      });
    }
  }, [state.transactionsLoading, dispatch]);
  
  const getTransactionsForInvoice = useCallback((invoiceId: string) => {
    return state.transactions[invoiceId] || [];
  }, [state.transactions]);
  
  const isLoadingTransactions = useCallback((invoiceId: string) => {
    return state.transactionsLoading[invoiceId] || false;
  }, [state.transactionsLoading]);
  
  const getTransactionError = useCallback((invoiceId: string) => {
    return state.transactionsError[invoiceId] || null;
  }, [state.transactionsError]);
  
  return {
    loadTransactions,
    getTransactionsForInvoice,
    isLoadingTransactions,
    getTransactionError,
  };
}

export function useCheckoutState() {
  const { state, dispatch } = usePaymentState();
  
  const setCheckout = useCallback((checkout: PayFastCheckoutResponse) => {
    dispatch({ type: 'CHECKOUT_SUCCESS', payload: checkout });
  }, [dispatch]);
  
  const clearCheckout = useCallback(() => {
    dispatch({ type: 'CHECKOUT_CLEAR' });
  }, [dispatch]);
  
  const setCheckoutError = useCallback((error: string) => {
    dispatch({ type: 'CHECKOUT_ERROR', payload: error });
  }, [dispatch]);
  
  return {
    currentCheckout: state.currentCheckout,
    checkoutLoading: state.checkoutLoading,
    checkoutError: state.checkoutError,
    setCheckout,
    clearCheckout,
    setCheckoutError,
  };
}

export function usePaymentUI() {
  const { state, dispatch } = usePaymentState();
  
  const setActiveInvoice = useCallback((invoiceId: string | null) => {
    dispatch({ type: 'SET_ACTIVE_INVOICE', payload: invoiceId });
  }, [dispatch]);
  
  const openPaymentMethodModal = useCallback(() => {
    dispatch({ type: 'SET_PAYMENT_METHOD_MODAL', payload: true });
  }, [dispatch]);
  
  const closePaymentMethodModal = useCallback(() => {
    dispatch({ type: 'SET_PAYMENT_METHOD_MODAL', payload: false });
  }, [dispatch]);
  
  const openInvoiceDetailModal = useCallback(() => {
    dispatch({ type: 'SET_INVOICE_DETAIL_MODAL', payload: true });
  }, [dispatch]);
  
  const closeInvoiceDetailModal = useCallback(() => {
    dispatch({ type: 'SET_INVOICE_DETAIL_MODAL', payload: false });
  }, [dispatch]);
  
  return {
    activeInvoiceId: state.activeInvoiceId,
    isPaymentMethodModalOpen: state.isPaymentMethodModalOpen,
    isInvoiceDetailModalOpen: state.isInvoiceDetailModalOpen,
    setActiveInvoice,
    openPaymentMethodModal,
    closePaymentMethodModal,
    openInvoiceDetailModal,
    closeInvoiceDetailModal,
  };
}

// Real-time payment status updates (WebSocket integration)
export function usePaymentStatusUpdates() {
  const { dispatch } = usePaymentState();
  
  useEffect(() => {
    // WebSocket connection for real-time payment updates
    // This would integrate with the existing WebSocket service
    const handlePaymentStatusUpdate = (event: any) => {
      if (event.type === 'payment_status_update') {
        dispatch({
          type: 'INVOICE_STATUS_UPDATE',
          payload: {
            invoiceId: event.data.invoiceId,
            status: event.data.status,
          }
        });
      }
    };
    
    // Note: This would integrate with the existing WebSocket service
    // window.addEventListener('websocket-message', handlePaymentStatusUpdate);
    
    return () => {
      // window.removeEventListener('websocket-message', handlePaymentStatusUpdate);
    };
  }, [dispatch]);
}