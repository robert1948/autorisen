import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext.jsx'
import { CapeAIContext } from '../context/CapeAIContext.jsx'
import { vi } from 'vitest'

// Mock AuthContext data
export const mockAuthContextValue = {
  user: {
    id: 1,
    email: 'test@example.com',
    full_name: 'Test User',
    user_role: 'client'
  },
  token: 'mock-jwt-token',
  login: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
  loading: false,
  error: null
}

// Mock CapeAI context data
export const mockCapeAIContextValue = {
  messages: [],
  isLoading: false,
  error: null,
  sendMessage: vi.fn(),
  clearMessages: vi.fn(),
  suggestions: [],
  getSuggestions: vi.fn()
}

// Custom render function with providers
export function renderWithProviders(
  ui,
  {
    authValue = mockAuthContextValue,
    capeAIValue = mockCapeAIContextValue,
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        <AuthContext.Provider value={authValue}>
          <CapeAIContext.Provider value={capeAIValue}>
            {children}
          </CapeAIContext.Provider>
        </AuthContext.Provider>
      </BrowserRouter>
    )
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// Custom render for components that only need router
export function renderWithRouter(ui, renderOptions = {}) {
  function Wrapper({ children }) {
    return <BrowserRouter>{children}</BrowserRouter>
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// Mock API responses
export const mockApiResponses = {
  login: {
    access_token: 'mock-jwt-token',
    token_type: 'bearer',
    user: mockAuthContextValue.user
  },
  register: {
    id: 1,
    email: 'test@example.com',
    full_name: 'Test User',
    user_role: 'client'
  },
  aiResponse: {
    response: 'Hello! I\'m CapeAI, ready to help you.',
    session_id: 'mock-session-id',
    context: {},
    actions: []
  },
  suggestions: {
    suggestions: [
      { text: 'Get started with AI development', action: '/ai-dev' },
      { text: 'Explore our platform features', action: '/features' },
      { text: 'Contact our support team', action: '/support' }
    ]
  }
}

// Test data generators
export const createMockUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  full_name: 'Test User',
  user_role: 'client',
  ...overrides
})

export const createMockMessage = (overrides = {}) => ({
  id: Date.now(),
  text: 'Test message',
  sender: 'user',
  timestamp: new Date().toISOString(),
  ...overrides
})

// Helper functions for testing async operations
export const waitForApiCall = () => new Promise(resolve => setTimeout(resolve, 0))

export const mockApiCall = (mockFn, response, delay = 0) => {
  return mockFn.mockImplementation(() =>
    new Promise(resolve => 
      setTimeout(() => resolve({ data: response }), delay)
    )
  )
}
