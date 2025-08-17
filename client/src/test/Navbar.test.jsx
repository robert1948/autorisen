/**
 * Task 1.1.5 Frontend Component Tests - Navbar Component Tests
 * =============================================================
 * 
 * Tests for Navbar React component
 * Testing navigation, authentication state, responsive behavior
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { renderWithProviders, mockAuthContextValue } from '../test/utils.jsx'

describe('Navbar Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render navigation links', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByText('CapeControl')).toBeInTheDocument()
      expect(screen.getByText('Home')).toBeInTheDocument()
      expect(screen.getByText('About')).toBeInTheDocument()
    })

    it('should render brand logo/name', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const brand = screen.getByText('CapeControl')
      expect(brand).toBeInTheDocument()
      expect(brand.closest('a')).toHaveAttribute('href', '/')
    })
  })

  describe('Authentication State - Logged Out', () => {
    it('should show login and register buttons when not authenticated', () => {
      const loggedOutContext = {
        ...mockAuthContextValue,
        isAuthenticated: false,
        user: null
      }
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: loggedOutContext 
          }) 
        }
      )
      
      expect(screen.getByText('Login')).toBeInTheDocument()
      expect(screen.getByText('Register')).toBeInTheDocument()
      expect(screen.queryByText('Logout')).not.toBeInTheDocument()
    })

    it('should have correct links for login and register', () => {
      const loggedOutContext = {
        ...mockAuthContextValue,
        isAuthenticated: false,
        user: null
      }
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: loggedOutContext 
          }) 
        }
      )
      
      expect(screen.getByText('Login').closest('a')).toHaveAttribute('href', '/login')
      expect(screen.getByText('Register').closest('a')).toHaveAttribute('href', '/register')
    })
  })

  describe('Authentication State - Logged In', () => {
    it('should show user info and logout when authenticated', () => {
      const loggedInContext = {
        ...mockAuthContextValue,
        isAuthenticated: true,
        user: { id: 1, email: 'test@example.com', name: 'Test User' }
      }
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: loggedInContext 
          }) 
        }
      )
      
      expect(screen.getByText('Test User')).toBeInTheDocument()
      expect(screen.getByText('Logout')).toBeInTheDocument()
      expect(screen.queryByText('Login')).not.toBeInTheDocument()
      expect(screen.queryByText('Register')).not.toBeInTheDocument()
    })

    it('should show user profile dropdown', async () => {
      const user = userEvent.setup()
      const loggedInContext = {
        ...mockAuthContextValue,
        isAuthenticated: true,
        user: { id: 1, email: 'test@example.com', name: 'Test User' }
      }
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: loggedInContext 
          }) 
        }
      )
      
      const userButton = screen.getByText('Test User')
      await user.click(userButton)
      
      expect(screen.getByText('Profile')).toBeInTheDocument()
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })

    it('should handle logout when logout button is clicked', async () => {
      const user = userEvent.setup()
      const mockLogout = vi.fn()
      const loggedInContext = {
        ...mockAuthContextValue,
        isAuthenticated: true,
        user: { id: 1, email: 'test@example.com', name: 'Test User' },
        logout: mockLogout
      }
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: loggedInContext 
          }) 
        }
      )
      
      const logoutButton = screen.getByText('Logout')
      await user.click(logoutButton)
      
      expect(mockLogout).toHaveBeenCalledTimes(1)
    })
  })

  describe('Navigation Links', () => {
    it('should highlight active page', () => {
      // Mock window.location
      Object.defineProperty(window, 'location', {
        value: { pathname: '/about' },
        writable: true
      })
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const aboutLink = screen.getByText('About').closest('a')
      expect(aboutLink).toHaveClass('active')
    })

    it('should navigate to correct pages', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByText('Home').closest('a')).toHaveAttribute('href', '/')
      expect(screen.getByText('About').closest('a')).toHaveAttribute('href', '/about')
    })
  })

  describe('CapeAI Integration', () => {
    it('should show CapeAI toggle button', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByRole('button', { name: /capeai/i })).toBeInTheDocument()
    })

    it('should toggle CapeAI chat when button is clicked', async () => {
      const user = userEvent.setup()
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const capeAIButton = screen.getByRole('button', { name: /capeai/i })
      
      // First click should open
      await user.click(capeAIButton)
      expect(screen.getByRole('dialog')).toBeInTheDocument()
      
      // Second click should close
      await user.click(capeAIButton)
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
  })

  describe('Responsive Behavior', () => {
    it('should show mobile menu toggle on small screens', () => {
      // Mock window.innerWidth
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768
      })
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByRole('button', { name: /menu/i })).toBeInTheDocument()
    })

    it('should toggle mobile menu when hamburger is clicked', async () => {
      const user = userEvent.setup()
      
      // Mock small screen
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768
      })
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const menuButton = screen.getByRole('button', { name: /menu/i })
      
      // Menu should be hidden initially
      expect(screen.getByTestId('mobile-menu')).toHaveClass('hidden')
      
      // Click should show menu
      await user.click(menuButton)
      expect(screen.getByTestId('mobile-menu')).not.toHaveClass('hidden')
      
      // Click again should hide menu
      await user.click(menuButton)
      expect(screen.getByTestId('mobile-menu')).toHaveClass('hidden')
    })

    it('should hide mobile menu on large screens', () => {
      // Mock large screen
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1024
      })
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.queryByRole('button', { name: /menu/i })).not.toBeInTheDocument()
    })
  })

  describe('Loading State', () => {
    it('should show loading state while checking authentication', () => {
      const loadingContext = {
        ...mockAuthContextValue,
        isLoading: true
      }
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: loadingContext 
          }) 
        }
      )
      
      expect(screen.getByTestId('nav-loading')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByRole('navigation')).toHaveAttribute('aria-label', 'Main navigation')
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      // Tab through navigation links
      await user.tab()
      expect(screen.getByText('CapeControl')).toHaveFocus()
      
      await user.tab()
      expect(screen.getByText('Home')).toHaveFocus()
      
      await user.tab()
      expect(screen.getByText('About')).toHaveFocus()
    })

    it('should announce login state changes to screen readers', () => {
      const { rerender } = render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      // Initially logged out
      expect(screen.getByText('Login')).toBeInTheDocument()
      
      // Change to logged in
      const loggedInContext = {
        ...mockAuthContextValue,
        isAuthenticated: true,
        user: { id: 1, email: 'test@example.com', name: 'Test User' }
      }
      
      rerender(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: loggedInContext 
          }) 
        }
      )
      
      expect(screen.getByText('Test User')).toBeInTheDocument()
      expect(screen.getByLabelText(/logged in as test user/i)).toBeInTheDocument()
    })
  })

  describe('Theme Support', () => {
    it('should adapt to dark theme', () => {
      // Mock dark theme
      document.documentElement.classList.add('dark')
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const navbar = screen.getByRole('navigation')
      expect(navbar).toHaveClass('dark:bg-gray-900')
      
      // Cleanup
      document.documentElement.classList.remove('dark')
    })
  })

  describe('Error Handling', () => {
    it('should handle authentication errors gracefully', () => {
      const errorContext = {
        ...mockAuthContextValue,
        error: 'Authentication failed'
      }
      
      render(
        <BrowserRouter>
          <Navbar />
        </BrowserRouter>,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            authValue: errorContext 
          }) 
        }
      )
      
      // Should still render navigation even with auth error
      expect(screen.getByText('CapeControl')).toBeInTheDocument()
      expect(screen.getByText('Home')).toBeInTheDocument()
    })
  })
})
