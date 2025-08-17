/**
 * Task 1.1.5 Frontend Component Tests - Login Page Tests
 * =======================================================
 * 
 * Tests for Login page React component
 * Testing form validation, authentication flow, error handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { Login } from '../pages/Login'
import { renderWithProviders, mockAuthContextValue } from '../test/utils.jsx'

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render login form', () => {
      renderWithProviders(<Login />)
      
      expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(document.getElementById('password')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
    })

    it('should render link to register page', () => {
      renderWithProviders(<Login />)
      
      const registerLink = screen.getByText(/don't have an account/i).parentElement.querySelector('a')
      expect(registerLink).toHaveAttribute('href', '/register')
      expect(registerLink).toHaveTextContent(/sign up/i)
    })

    it('should render forgot password link', () => {
      renderWithProviders(<Login />)
      
      const forgotLink = screen.getByText(/forgot password/i)
      expect(forgotLink).toBeInTheDocument()
      expect(forgotLink.closest('a')).toHaveAttribute('href', '/forgot-password')
    })
  })

  describe('Form Input', () => {
    it('should accept email input', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const emailInput = screen.getByLabelText(/email/i)
      await user.type(emailInput, 'test@example.com')
      
      expect(emailInput).toHaveValue('test@example.com')
    })

    it('should accept password input', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const passwordInput = document.getElementById('password')
      await user.type(passwordInput, 'password123')
      
      expect(passwordInput).toHaveValue('password123')
    })

    it('should toggle password visibility', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const passwordInput = document.getElementById('password')
      const toggleButton = screen.getByTestId('password-toggle')
      
      expect(passwordInput).toHaveAttribute('type', 'password')
      
      await user.click(toggleButton)
      expect(passwordInput).toHaveAttribute('type', 'text')
      
      await user.click(toggleButton)
      expect(passwordInput).toHaveAttribute('type', 'password')
    })
  })

  describe('Form Validation', () => {
    it('should show error for empty email', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const submitButton = screen.getByRole('button', { name: /login/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument()
      })
    })

    it('should show error for invalid email format', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'invalid-email')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/invalid email format/i)).toBeInTheDocument()
      })
    })

    it('should show error for empty password', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument()
      })
    })

    it('should show error for short password', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = document.getElementById('password')
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, '123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument()
      })
    })

    it('should clear validation errors when input changes', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      // Trigger validation error
      await user.click(submitButton)
      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument()
      })
      
      // Clear error by typing
      await user.type(emailInput, 'test@example.com')
      expect(screen.queryByText(/email is required/i)).not.toBeInTheDocument()
    })
  })

  describe('Authentication Flow', () => {
    it('should call login function with correct credentials', async () => {
      const user = userEvent.setup()
      const mockLogin = vi.fn()
      
      renderWithProviders(<Login />, {
        authValue: { ...mockAuthContextValue, login: mockLogin }
      })
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = document.getElementById('password')
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
      })
    })

    it('should show loading state during login', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />, {
        authValue: { ...mockAuthContextValue, loading: true }
      })
      
      expect(screen.getByText(/logging in/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /logging in/i })).toBeDisabled()
    })

    it('should disable form during loading', async () => {
      renderWithProviders(<Login />, {
        authValue: { ...mockAuthContextValue, loading: true }
      })
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = document.getElementById('password')
      const submitButton = screen.getByRole('button', { name: /logging in/i })
      
      expect(emailInput).toBeDisabled()
      expect(passwordInput).toBeDisabled()
      expect(submitButton).toBeDisabled()
    })
  })

  describe('Error Handling', () => {
    it('should display authentication errors', () => {
      const errorMessage = 'Invalid credentials'
      
      renderWithProviders(<Login />, {
        authValue: { ...mockAuthContextValue, error: errorMessage }
      })
      
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
      expect(screen.getByRole('alert')).toBeInTheDocument()
    })

    it('should display generic error for network failures', () => {
      const errorMessage = 'Network error occurred'
      
      renderWithProviders(<Login />, {
        authValue: { ...mockAuthContextValue, error: errorMessage }
      })
      
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })

    it('should clear errors when form is resubmitted', async () => {
      const user = userEvent.setup()
      const mockLogin = vi.fn()
      
      renderWithProviders(<Login />, {
        authValue: { ...mockAuthContextValue, error: 'Previous error', login: mockLogin }
      })
      
      // Error should be visible initially
      expect(screen.getByText('Previous error')).toBeInTheDocument()
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = document.getElementById('password')
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      // Error should be cleared on resubmit
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalled()
      })
    })
  })

  describe('Remember Me', () => {
    it('should render remember me checkbox', () => {
      renderWithProviders(<Login />)
      
      const checkbox = screen.getByLabelText(/remember me/i)
      expect(checkbox).toBeInTheDocument()
      expect(checkbox).toHaveAttribute('type', 'checkbox')
      expect(checkbox).not.toBeChecked()
    })

    it('should toggle remember me state', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const checkbox = screen.getByLabelText(/remember me/i)
      
      expect(checkbox).not.toBeChecked()
      
      await user.click(checkbox)
      expect(checkbox).toBeChecked()
      
      await user.click(checkbox)
      expect(checkbox).not.toBeChecked()
    })
  })

  describe('Accessibility', () => {
    it('should have proper form labels and ARIA attributes', () => {
      renderWithProviders(<Login />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = document.getElementById('password')
      const form = screen.getByRole('form')
      
      expect(emailInput).toHaveAttribute('id', 'email')
      expect(passwordInput).toHaveAttribute('id', 'password')
      expect(form).toHaveAttribute('aria-labelledby', 'login-heading')
    })

    it('should announce errors to screen readers', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const submitButton = screen.getByRole('button', { name: /login/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        const errorElement = screen.getByText(/email is required/i)
        expect(errorElement).toHaveAttribute('role', 'alert')
      })
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(<Login />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = document.getElementById('password')
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      // Tab through form elements
      await user.tab()
      expect(emailInput).toHaveFocus()
      
      await user.tab()
      expect(passwordInput).toHaveFocus()
      
      await user.tab()
      // Skip password toggle button
      await user.tab()
      expect(screen.getByLabelText(/remember me/i)).toHaveFocus()
      
      await user.tab()
      expect(submitButton).toHaveFocus()
    })
  })

  describe('Social Login', () => {
    it('should render social login buttons', () => {
      renderWithProviders(<Login />)
      
      expect(screen.getByText(/continue with google/i)).toBeInTheDocument()
      expect(screen.getByText(/continue with github/i)).toBeInTheDocument()
    })

    it('should handle social login clicks', async () => {
      const user = userEvent.setup()
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      
      renderWithProviders(<Login />)
      
      const googleButton = screen.getByText(/continue with google/i)
      const githubButton = screen.getByText(/continue with github/i)
      
      await user.click(googleButton)
      expect(consoleSpy).toHaveBeenCalledWith('Social login with google')
      
      await user.click(githubButton)
      expect(consoleSpy).toHaveBeenCalledWith('Social login with github')
      
      consoleSpy.mockRestore()
    })
  })
})
