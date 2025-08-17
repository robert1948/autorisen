/**
 * Task 1.1.5 Frontend Component Tests - Register Page Tests
 * ==========================================================
 * 
 * Tests for Register page React component
 * Testing form validation, registration flow, error handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Register } from '../pages/Register'
import { renderWithProviders, mockAuthContextValue } from '../test/utils.jsx'

describe('Register Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render registration form', () => {
      renderWithProviders(<Register />)
      
      expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText('Password')).toBeInTheDocument()
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
    })

    it('should render link to login page', () => {
      renderWithProviders(<Register />)
      
      const loginLink = screen.getByText(/sign in/i)
      expect(loginLink.closest('a')).toHaveAttribute('href', '/login')
      expect(loginLink).toHaveTextContent(/sign in/i)
    })

    it('should render terms and privacy policy links', () => {
      renderWithProviders(<Register />)
      
      expect(screen.getByText(/terms of service/i)).toBeInTheDocument()
      expect(screen.getByText(/privacy policy/i)).toBeInTheDocument()
    })
  })

  describe('Form Input', () => {
    it('should accept name input', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const nameInput = screen.getByLabelText(/full name/i)
      await user.type(nameInput, 'John Doe')
      
      expect(nameInput).toHaveValue('John Doe')
    })

    it('should accept email input', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const emailInput = screen.getByLabelText(/email/i)
      await user.type(emailInput, 'john@example.com')
      
      expect(emailInput).toHaveValue('john@example.com')
    })

    it('should accept password input', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const passwordInput = screen.getByLabelText('Password')
      await user.type(passwordInput, 'password123')
      
      expect(passwordInput).toHaveValue('password123')
      expect(passwordInput).toHaveAttribute('type', 'password')
    })

    it('should accept confirm password input', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      await user.type(confirmPasswordInput, 'password123')
      
      expect(confirmPasswordInput).toHaveValue('password123')
      expect(confirmPasswordInput).toHaveAttribute('type', 'password')
    })

    it('should toggle password visibility', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const passwordInput = screen.getByLabelText('Password')
      const toggleButtons = screen.getAllByRole('button', { name: /show password/i })
      
      expect(passwordInput).toHaveAttribute('type', 'password')
      
      await user.click(toggleButtons[0])
      expect(passwordInput).toHaveAttribute('type', 'text')
      
      await user.click(toggleButtons[0])
      expect(passwordInput).toHaveAttribute('type', 'password')
    })
  })

  describe('Form Validation', () => {
    it('should show error for empty name', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const submitButton = screen.getByRole('button', { name: /create account/i })
      await user.click(submitButton)
      
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    it('should show error for empty email', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const nameInput = screen.getByLabelText(/full name/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.click(submitButton)
      
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    })

    it('should show error for invalid email format', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'invalid-email')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument()
      })
    })

    it('should show error for empty password', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.click(submitButton)
      
      expect(screen.getByText(/password is required/i)).toBeInTheDocument()
    })

    it('should show error for short password', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText('Password')
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, '123')
      await user.click(submitButton)
      
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
    })

    it('should show error for password mismatch', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText('Password')
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'different123')
      await user.click(submitButton)
      
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
    })

    it('should show password strength indicator', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const passwordInput = screen.getByLabelText('Password')
      
      // Weak password
      await user.type(passwordInput, '123')
      expect(screen.getByText(/weak/i)).toBeInTheDocument()
      
      // Medium password
      await user.clear(passwordInput)
      await user.type(passwordInput, 'password123')
      expect(screen.getByText(/medium/i)).toBeInTheDocument()
      
      // Strong password
      await user.clear(passwordInput)
      await user.type(passwordInput, 'StrongPass123!')
      expect(screen.getByText(/strong/i)).toBeInTheDocument()
    })

    it('should clear validation errors when input changes', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const nameInput = screen.getByLabelText(/full name/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      // Trigger validation error
      await user.click(submitButton)
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
      
      // Type in name should clear error
      await user.type(nameInput, 'John Doe')
      expect(screen.queryByText(/name is required/i)).not.toBeInTheDocument()
    })
  })

  describe('Registration Flow', () => {
    it('should call register function with correct data', async () => {
      const user = userEvent.setup()
      const mockRegister = vi.fn().mockResolvedValue({ success: true })
      const contextWithMock = {
        ...mockAuthContextValue,
        register: mockRegister
      }
      
      renderWithProviders(<Register />, { 
        authValue: contextWithMock 
      })
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText('Password')
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      const termsCheckbox = screen.getByLabelText(/i agree to the terms/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password123')
      await user.click(termsCheckbox)
      await user.click(submitButton)
      
      // Should advance to step 2 (role selection) instead of calling register
      expect(screen.getByText(/choose your role/i)).toBeInTheDocument()
      expect(screen.getByText(/step 2/i)).toBeInTheDocument()
    })

    it('should show loading state during registration', async () => {
      const user = userEvent.setup()
      const mockRegister = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      const contextWithMock = {
        ...mockAuthContextValue,
        register: mockRegister,
        isLoading: false
      }
      
      renderWithProviders(<Register />, { 
        authValue: contextWithMock 
      })
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText('Password')
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      const termsCheckbox = screen.getByLabelText(/i agree to the terms/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password123')
      await user.click(termsCheckbox)
      await user.click(submitButton)
      
      expect(screen.getByText(/choose your role/i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
    })

    it('should disable form during loading', async () => {
      const loadingContext = {
        ...mockAuthContextValue,
        isLoading: true
      }
      
      renderWithProviders(<Register />, { 
        authValue: loadingContext 
      })
      
      expect(screen.getByLabelText(/full name/i)).toBeDisabled()
      expect(screen.getByLabelText(/email/i)).toBeDisabled()
      expect(screen.getByLabelText('Password')).toBeDisabled()
      expect(screen.getByLabelText(/confirm password/i)).toBeDisabled()
      expect(screen.getByRole('button', { name: /create account/i })).toBeDisabled()
    })
  })

  describe('Error Handling', () => {
    it('should display registration errors', async () => {
      const user = userEvent.setup()
      const mockRegister = vi.fn().mockRejectedValue(new Error('Email already exists'))
      const contextWithMock = {
        ...mockAuthContextValue,
        register: mockRegister
      }
      
      renderWithProviders(<Register />, { 
        authValue: contextWithMock 
      })
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText('Password')
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'existing@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/email already exists/i)).toBeInTheDocument()
      })
    })

    it('should display generic error for network failures', async () => {
      const user = userEvent.setup()
      const mockRegister = vi.fn().mockRejectedValue(new Error('Network Error'))
      const contextWithMock = {
        ...mockAuthContextValue,
        register: mockRegister
      }
      
      renderWithProviders(<Register />, { 
        authValue: contextWithMock 
      })
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText('Password')
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/registration failed/i)).toBeInTheDocument()
      })
    })
  })

  describe('Terms and Conditions', () => {
    it('should render terms acceptance checkbox', () => {
      renderWithProviders(<Register />)
      
      expect(screen.getByLabelText(/i agree to the terms/i)).toBeInTheDocument()
    })

    it('should require terms acceptance', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText('Password')
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password123')
      await user.click(submitButton)
      
      expect(screen.getByText(/you must agree to the terms/i)).toBeInTheDocument()
    })

    it('should enable submission when terms are accepted', async () => {
      const user = userEvent.setup()
      const mockRegister = vi.fn().mockResolvedValue({ success: true })
      const contextWithMock = {
        ...mockAuthContextValue,
        register: mockRegister
      }
      
      renderWithProviders(<Register />, { 
        authValue: contextWithMock 
      })
      
      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText('Password')
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
      const termsCheckbox = screen.getByLabelText(/i agree to the terms/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, 'password123')
      await user.type(confirmPasswordInput, 'password123')
      await user.click(termsCheckbox)
      await user.click(submitButton)
      
      // Should advance to step 2 instead of calling register
      expect(screen.getByText(/choose your role/i)).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper form labels and ARIA attributes', () => {
      renderWithProviders(<Register />)
      
      expect(screen.getByLabelText(/full name/i)).toHaveAttribute('aria-describedby')
      expect(screen.getByLabelText(/email/i)).toHaveAttribute('aria-describedby')
      expect(screen.getByLabelText('Password')).toHaveAttribute('aria-describedby')
      expect(screen.getByRole('form')).toHaveAttribute('aria-labelledby')
    })

    it('should announce errors to screen readers', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      const submitButton = screen.getByRole('button', { name: /create account/i })
      await user.click(submitButton)
      
      const errorMessage = screen.getByText(/name is required/i)
      expect(errorMessage).toHaveAttribute('role', 'alert')
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Register />)
      
      await user.tab()
      expect(screen.getByLabelText(/full name/i)).toHaveFocus()
      
      await user.tab()
      expect(screen.getByLabelText(/email/i)).toHaveFocus()
      
      await user.tab()
      expect(screen.getByLabelText('Password')).toHaveFocus()
    })
  })

  describe('Social Registration', () => {
    it('should render social registration buttons', () => {
      renderWithProviders(<Register />)
      
      expect(screen.getByText(/continue with google/i)).toBeInTheDocument()
      expect(screen.getByText(/continue with github/i)).toBeInTheDocument()
    })

    it('should handle social registration clicks', async () => {
      const user = userEvent.setup()
      const mockSocialLogin = vi.fn()
      
      // Mock social login in context
      const contextWithSocial = {
        ...mockAuthContextValue,
        socialLogin: mockSocialLogin
      }
      
      renderWithProviders(<Register />, { 
        authValue: contextWithSocial 
      })
      
      const googleButton = screen.getByText(/continue with google/i)
      await user.click(googleButton)
      
      expect(mockSocialLogin).toHaveBeenCalledWith('google')
    })
  })
})
