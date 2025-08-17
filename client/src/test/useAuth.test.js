/**
 * Task 1.1.5 Frontend Component Tests - Authentication Hook Tests
 * ============================================================
 * 
 * Tests for useAuth custom hook functionality
 * Testing authentication state management, login/logout operations
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { mockApiResponses, mockApiCall } from '../test/utils.jsx'

// Mock axios
const mockAxios = {
  post: vi.fn(),
  get: vi.fn(),
  create: vi.fn(() => mockAxios)
}

vi.mock('axios', () => ({
  default: mockAxios
}))

// Wrapper component for testing hooks with router
const wrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>

describe('useAuth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    sessionStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with default state when no stored token', () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('should load user from localStorage if token exists', async () => {
      const mockToken = 'stored-jwt-token'
      const mockUser = { id: 1, email: 'stored@example.com' }
      
      localStorage.setItem('auth_token', mockToken)
      localStorage.setItem('user_data', JSON.stringify(mockUser))
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      expect(result.current.token).toBe(mockToken)
      expect(result.current.user).toEqual(mockUser)
    })
  })

  describe('Login Function', () => {
    it('should successfully login with valid credentials', async () => {
      mockApiCall(mockAxios.post, mockApiResponses.login)
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      await act(async () => {
        await result.current.login('test@example.com', 'password123')
      })
      
      expect(result.current.user).toEqual(mockApiResponses.login.user)
      expect(result.current.token).toBe(mockApiResponses.login.access_token)
      expect(result.current.error).toBeNull()
      expect(localStorage.getItem('auth_token')).toBe(mockApiResponses.login.access_token)
    })

    it('should handle login failure with error message', async () => {
      const errorMessage = 'Invalid credentials'
      mockAxios.post.mockRejectedValue({
        response: { data: { detail: errorMessage } }
      })
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      await act(async () => {
        await result.current.login('invalid@example.com', 'wrongpassword')
      })
      
      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(result.current.error).toBe(errorMessage)
    })

    it('should set loading state during login process', async () => {
      let resolveLogin
      mockAxios.post.mockReturnValue(new Promise(resolve => {
        resolveLogin = resolve
      }))
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      act(() => {
        result.current.login('test@example.com', 'password123')
      })
      
      expect(result.current.loading).toBe(true)
      
      await act(async () => {
        resolveLogin({ data: mockApiResponses.login })
      })
      
      expect(result.current.loading).toBe(false)
    })
  })

  describe('Register Function', () => {
    it('should successfully register new user', async () => {
      mockApiCall(mockAxios.post, mockApiResponses.register)
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      const userData = {
        email: 'new@example.com',
        password: 'password123',
        full_name: 'New User',
        user_role: 'client'
      }
      
      await act(async () => {
        await result.current.register(userData)
      })
      
      expect(mockAxios.post).toHaveBeenCalledWith('/api/auth/v2/register', userData)
      expect(result.current.error).toBeNull()
    })

    it('should handle registration validation errors', async () => {
      const validationError = 'Email already exists'
      mockAxios.post.mockRejectedValue({
        response: { data: { detail: validationError } }
      })
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      await act(async () => {
        await result.current.register({
          email: 'existing@example.com',
          password: 'password123'
        })
      })
      
      expect(result.current.error).toBe(validationError)
    })
  })

  describe('Logout Function', () => {
    it('should clear user data and token on logout', async () => {
      // Set initial logged-in state
      localStorage.setItem('auth_token', 'test-token')
      localStorage.setItem('user_data', JSON.stringify({ id: 1, email: 'test@example.com' }))
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      act(() => {
        result.current.logout()
      })
      
      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
      expect(localStorage.getItem('auth_token')).toBeNull()
      expect(localStorage.getItem('user_data')).toBeNull()
    })
  })

  describe('Token Validation', () => {
    it('should validate stored token on initialization', async () => {
      const mockToken = 'valid-token'
      const mockUser = { id: 1, email: 'test@example.com' }
      
      localStorage.setItem('auth_token', mockToken)
      mockApiCall(mockAxios.get, mockUser)
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      // Wait for token validation
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0))
      })
      
      expect(result.current.user).toEqual(mockUser)
    })

    it('should logout if token validation fails', async () => {
      const invalidToken = 'invalid-token'
      localStorage.setItem('auth_token', invalidToken)
      
      mockAxios.get.mockRejectedValue({
        response: { status: 401 }
      })
      
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      // Wait for token validation
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0))
      })
      
      expect(result.current.user).toBeNull()
      expect(result.current.token).toBeNull()
    })
  })

  describe('Error Handling', () => {
    it('should clear errors when starting new operations', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      
      // Set an error state
      mockAxios.post.mockRejectedValue({
        response: { data: { detail: 'Login failed' } }
      })
      
      await act(async () => {
        await result.current.login('test@example.com', 'wrong')
      })
      
      expect(result.current.error).toBe('Login failed')
      
      // Clear error on new login attempt
      mockApiCall(mockAxios.post, mockApiResponses.login)
      
      await act(async () => {
        await result.current.login('test@example.com', 'correct')
      })
      
      expect(result.current.error).toBeNull()
    })
  })
})
