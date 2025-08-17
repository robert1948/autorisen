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
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
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
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      await user.type(emailInput, 'test@example.com')
      
      expect(emailInput).toHaveValue('test@example.com')
    })

    it('should accept password input', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const passwordInput = screen.getByLabelText(/password/i)
      await user.type(passwordInput, 'password123')
      
      expect(passwordInput).toHaveValue('password123')
      expect(passwordInput).toHaveAttribute('type', 'password')
    })

    it('should toggle password visibility', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const passwordInput = screen.getByLabelText(/password/i)
      const toggleButton = screen.getByRole('button', { name: /show password/i })
      
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
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const submitButton = screen.getByRole('button', { name: /login/i })
      await user.click(submitButton)
      
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    })

    it('should show error for invalid email format', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'invalid-email')
      await user.click(submitButton)
      
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument()
    })

    it('should show error for empty password', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.click(submitButton)
      
      expect(screen.getByText(/password is required/i)).toBeInTheDocument()
    })

    it('should show error for short password', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, '123')
      await user.click(submitButton)
      
      expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument()
    })

    it('should clear validation errors when input changes', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      // Trigger validation error
      await user.click(submitButton)
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
      
      // Type in email should clear error
      await user.type(emailInput, 'test@example.com')
      expect(screen.queryByText(/email is required/i)).not.toBeInTheDocument()
    })
  })

  describe('Authentication Flow', () => {
    it('should call login function with correct credentials', async () => {
      const user = userEvent.setup()
      const mockLogin = vi.fn().mockResolvedValue({ success: true })
      const contextWithMock = {
        ...mockAuthContextValue,
        login: mockLogin
      }
      
      renderWithProviders(
<Login />
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: contextWithMock 
          }) 
        }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
    })

    it('should show loading state during login', async () => {
      const user = userEvent.setup()
      const mockLogin = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      const contextWithMock = {
        ...mockAuthContextValue,
        login: mockLogin,
        isLoading: false
      }
      
      renderWithProviders(
<Login />
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: contextWithMock 
          }) 
        }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      expect(screen.getByText(/logging in/i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
    })

    it('should disable form during loading', async () => {
      const loadingContext = {
        ...mockAuthContextValue,
        isLoading: true
      }
      
      renderWithProviders(
<Login />
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: loadingContext 
          }) 
        }
      )
      
      expect(screen.getByLabelText(/email/i)).toBeDisabled()
      expect(screen.getByLabelText(/password/i)).toBeDisabled()
      expect(screen.getByRole('button', { name: /login/i })).toBeDisabled()
    })
  })

  describe('Error Handling', () => {
    it('should display authentication errors', async () => {
      const user = userEvent.setup()
      const mockLogin = vi.fn().mockRejectedValue(new Error('Invalid credentials'))
      const contextWithMock = {
        ...mockAuthContextValue,
        login: mockLogin
      }
      
      renderWithProviders(
<Login />
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: contextWithMock 
          }) 
        }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'wrongpassword')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
      })
    })

    it('should display generic error for network failures', async () => {
      const user = userEvent.setup()
      const mockLogin = vi.fn().mockRejectedValue(new Error('Network Error'))
      const contextWithMock = {
        ...mockAuthContextValue,
        login: mockLogin
      }
      
      renderWithProviders(
<Login />
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: contextWithMock 
          }) 
        }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/login failed/i)).toBeInTheDocument()
      })
    })

    it('should clear errors when form is resubmitted', async () => {
      const user = userEvent.setup()
      let callCount = 0
      const mockLogin = vi.fn().mockImplementation(() => {
        callCount++
        if (callCount === 1) {
          return Promise.reject(new Error('Invalid credentials'))
        }
        return Promise.resolve({ success: true })
      })
      const contextWithMock = {
        ...mockAuthContextValue,
        login: mockLogin
      }
      
      renderWithProviders(
<Login />
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: contextWithMock 
          }) 
        }
      )
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /login/i })
      
      // First attempt - should fail
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'wrongpassword')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
      })
      
      // Second attempt - should clear error
      await user.clear(passwordInput)
      await user.type(passwordInput, 'correctpassword')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.queryByText(/invalid credentials/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('Remember Me', () => {
    it('should render remember me checkbox', () => {
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByLabelText(/remember me/i)).toBeInTheDocument()
    })

    it('should toggle remember me state', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const rememberCheckbox = screen.getByLabelText(/remember me/i)
      
      expect(rememberCheckbox).not.toBeChecked()
      
      await user.click(rememberCheckbox)
      expect(rememberCheckbox).toBeChecked()
      
      await user.click(rememberCheckbox)
      expect(rememberCheckbox).not.toBeChecked()
    })
  })

  describe('Accessibility', () => {
    it('should have proper form labels and ARIA attributes', () => {
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByLabelText(/email/i)).toHaveAttribute('aria-describedby')
      expect(screen.getByLabelText(/password/i)).toHaveAttribute('aria-describedby')
      expect(screen.getByRole('form')).toHaveAttribute('aria-labelledby')
    })

    it('should announce errors to screen readers', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const submitButton = screen.getByRole('button', { name: /login/i })
      await user.click(submitButton)
      
      const errorMessage = screen.getByText(/email is required/i)
      expect(errorMessage).toHaveAttribute('role', 'alert')
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()
      
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      await user.tab()
      expect(screen.getByLabelText(/email/i)).toHaveFocus()
      
      await user.tab()
      expect(screen.getByLabelText(/password/i)).toHaveFocus()
      
      await user.tab()
      expect(screen.getByLabelText(/remember me/i)).toHaveFocus()
      
      await user.tab()
      expect(screen.getByRole('button', { name: /login/i })).toHaveFocus()
    })
  })

  describe('Social Login', () => {
    it('should render social login buttons', () => {
      renderWithProviders(
<Login />
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByText(/continue with google/i)).toBeInTheDocument()
      expect(screen.getByText(/continue with github/i)).toBeInTheDocument()
    })

    it('should handle social login clicks', async () => {
      const user = userEvent.setup()
      const mockSocialLogin = vi.fn()
      
      // Mock social login in context
      const contextWithSocial = {
        ...mockAuthContextValue,
        socialLogin: mockSocialLogin
      }
      
      renderWithProviders(
<Login />
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: contextWithSocial 
          }) 
        }
      )
      
      const googleButton = screen.getByText(/continue with google/i)
      await user.click(googleButton)
      
      expect(mockSocialLogin).toHaveBeenCalledWith('google')
    })
  })
})
