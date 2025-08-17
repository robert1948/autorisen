/**
 * Task 1.1.5 Frontend Component Tests - CapeAI Chat Component Tests
 * ================================================================
 * 
 * Tests for CapeAIChat React component
 * Testing chat interface, message display, user interactions
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { CapeAIChat } from '../components/CapeAIChat'
import { renderWithProviders, mockCapeAIContextValue } from '../test/utils.jsx'

describe('CapeAIChat Component', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render chat interface when open', () => {
      render(
        <CapeAIChat {...defaultProps} />,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByRole('dialog')).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/ask me anything/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
    })

    it('should not render when closed', () => {
      render(
        <CapeAIChat {...defaultProps} isOpen={false} />,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('should display welcome message initially', () => {
      render(
        <CapeAIChat {...defaultProps} />,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByText(/hello! i'm capeai/i)).toBeInTheDocument()
    })
  })

  describe('Message Display', () => {
    it('should display existing messages from context', () => {
      const messagesContext = {
        ...mockCapeAIContextValue,
        messages: [
          { id: 1, text: 'Hello CapeAI', sender: 'user', timestamp: new Date().toISOString() },
          { id: 2, text: 'Hello! How can I help?', sender: 'ai', timestamp: new Date().toISOString() }
        ]
      }

      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: messagesContext 
          }) 
        }
      )
      
      expect(screen.getByText('Hello CapeAI')).toBeInTheDocument()
      expect(screen.getByText('Hello! How can I help?')).toBeInTheDocument()
    })

    it('should distinguish between user and AI messages visually', () => {
      const messagesContext = {
        ...mockCapeAIContextValue,
        messages: [
          { id: 1, text: 'User message', sender: 'user', timestamp: new Date().toISOString() },
          { id: 2, text: 'AI response', sender: 'ai', timestamp: new Date().toISOString() }
        ]
      }

      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: messagesContext 
          }) 
        }
      )
      
      const userMessage = screen.getByText('User message').closest('.message')
      const aiMessage = screen.getByText('AI response').closest('.message')
      
      expect(userMessage).toHaveClass('user-message')
      expect(aiMessage).toHaveClass('ai-message')
    })
  })

  describe('Message Input', () => {
    it('should accept user input in the text field', async () => {
      const user = userEvent.setup()
      
      render(
        <CapeAIChat {...defaultProps} />,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const input = screen.getByPlaceholderText(/ask me anything/i)
      await user.type(input, 'Test message')
      
      expect(input).toHaveValue('Test message')
    })

    it('should send message when Send button is clicked', async () => {
      const user = userEvent.setup()
      const mockSendMessage = vi.fn()
      const contextWithMock = {
        ...mockCapeAIContextValue,
        sendMessage: mockSendMessage
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: contextWithMock 
          }) 
        }
      )
      
      const input = screen.getByPlaceholderText(/ask me anything/i)
      const sendButton = screen.getByRole('button', { name: /send/i })
      
      await user.type(input, 'Hello CapeAI!')
      await user.click(sendButton)
      
      expect(mockSendMessage).toHaveBeenCalledWith('Hello CapeAI!')
      expect(input).toHaveValue('') // Should clear after sending
    })

    it('should send message when Enter key is pressed', async () => {
      const user = userEvent.setup()
      const mockSendMessage = vi.fn()
      const contextWithMock = {
        ...mockCapeAIContextValue,
        sendMessage: mockSendMessage
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: contextWithMock 
          }) 
        }
      )
      
      const input = screen.getByPlaceholderText(/ask me anything/i)
      
      await user.type(input, 'Hello CapeAI!')
      await user.keyboard('{Enter}')
      
      expect(mockSendMessage).toHaveBeenCalledWith('Hello CapeAI!')
    })

    it('should not send empty messages', async () => {
      const user = userEvent.setup()
      const mockSendMessage = vi.fn()
      const contextWithMock = {
        ...mockCapeAIContextValue,
        sendMessage: mockSendMessage
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: contextWithMock 
          }) 
        }
      )
      
      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)
      
      expect(mockSendMessage).not.toHaveBeenCalled()
    })

    it('should not send whitespace-only messages', async () => {
      const user = userEvent.setup()
      const mockSendMessage = vi.fn()
      const contextWithMock = {
        ...mockCapeAIContextValue,
        sendMessage: mockSendMessage
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: contextWithMock 
          }) 
        }
      )
      
      const input = screen.getByPlaceholderText(/ask me anything/i)
      const sendButton = screen.getByRole('button', { name: /send/i })
      
      await user.type(input, '   ')
      await user.click(sendButton)
      
      expect(mockSendMessage).not.toHaveBeenCalled()
    })
  })

  describe('Loading State', () => {
    it('should show loading indicator when AI is processing', () => {
      const loadingContext = {
        ...mockCapeAIContextValue,
        isLoading: true
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: loadingContext 
          }) 
        }
      )
      
      expect(screen.getByText(/thinking/i)).toBeInTheDocument()
    })

    it('should disable input and send button while loading', () => {
      const loadingContext = {
        ...mockCapeAIContextValue,
        isLoading: true
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: loadingContext 
          }) 
        }
      )
      
      expect(screen.getByPlaceholderText(/ask me anything/i)).toBeDisabled()
      expect(screen.getByRole('button', { name: /send/i })).toBeDisabled()
    })
  })

  describe('Error Handling', () => {
    it('should display error messages', () => {
      const errorContext = {
        ...mockCapeAIContextValue,
        error: 'Failed to connect to AI service'
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: errorContext 
          }) 
        }
      )
      
      expect(screen.getByText(/failed to connect to ai service/i)).toBeInTheDocument()
    })

    it('should allow retry after error', async () => {
      const user = userEvent.setup()
      const mockSendMessage = vi.fn()
      const errorContext = {
        ...mockCapeAIContextValue,
        error: 'Network error',
        sendMessage: mockSendMessage
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: errorContext 
          }) 
        }
      )
      
      const input = screen.getByPlaceholderText(/ask me anything/i)
      const sendButton = screen.getByRole('button', { name: /send/i })
      
      await user.type(input, 'Retry message')
      await user.click(sendButton)
      
      expect(mockSendMessage).toHaveBeenCalledWith('Retry message')
    })
  })

  describe('Chat Controls', () => {
    it('should call onClose when close button is clicked', async () => {
      const user = userEvent.setup()
      const mockOnClose = vi.fn()
      
      render(
        <CapeAIChat {...defaultProps} onClose={mockOnClose} />,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const closeButton = screen.getByRole('button', { name: /close/i })
      await user.click(closeButton)
      
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('should clear messages when clear button is clicked', async () => {
      const user = userEvent.setup()
      const mockClearMessages = vi.fn()
      const contextWithClear = {
        ...mockCapeAIContextValue,
        clearMessages: mockClearMessages,
        messages: [
          { id: 1, text: 'Test message', sender: 'user', timestamp: new Date().toISOString() }
        ]
      }
      
      render(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: contextWithClear 
          }) 
        }
      )
      
      const clearButton = screen.getByRole('button', { name: /clear/i })
      await user.click(clearButton)
      
      expect(mockClearMessages).toHaveBeenCalledTimes(1)
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(
        <CapeAIChat {...defaultProps} />,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      expect(screen.getByRole('dialog')).toHaveAttribute('aria-label', 'CapeAI Chat')
      expect(screen.getByPlaceholderText(/ask me anything/i)).toHaveAttribute('aria-label', 'Chat message input')
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()
      
      render(
        <CapeAIChat {...defaultProps} />,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const input = screen.getByPlaceholderText(/ask me anything/i)
      const sendButton = screen.getByRole('button', { name: /send/i })
      
      await user.tab()
      expect(input).toHaveFocus()
      
      await user.tab()
      expect(sendButton).toHaveFocus()
    })
  })

  describe('Message Scrolling', () => {
    it('should scroll to bottom when new messages are added', async () => {
      const scrollIntoViewMock = vi.fn()
      window.HTMLElement.prototype.scrollIntoView = scrollIntoViewMock
      
      const { rerender } = render(
        <CapeAIChat {...defaultProps} />,
        { wrapper: (props) => renderWithProviders(props.children) }
      )
      
      const newMessagesContext = {
        ...mockCapeAIContextValue,
        messages: [
          { id: 1, text: 'New message', sender: 'user', timestamp: new Date().toISOString() }
        ]
      }
      
      rerender(
        <CapeAIChat {...defaultProps} />,
        { 
          wrapper: (props) => renderWithProviders(props.children, { 
            capeAIValue: newMessagesContext 
          }) 
        }
      )
      
      await waitFor(() => {
        expect(scrollIntoViewMock).toHaveBeenCalled()
      })
    })
  })
})
