/**
 * Task 1.1.5 Frontend Component Tests - CapeAI Hook Tests
 * =======================================================
 * 
 * Tests for useCapeAI custom hook functionality
 * Testing AI chat functionality, message handling, suggestions
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { useCapeAI } from '../hooks/useCapeAI'
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

// Mock AuthContext
const mockAuthContext = {
  user: { id: 1, email: 'test@example.com' },
  token: 'mock-token'
}

vi.mock('../context/AuthContext', () => ({
  useAuth: () => mockAuthContext
}))

const wrapper = ({ children }) => <BrowserRouter>{children}</BrowserRouter>

describe('useCapeAI Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with empty messages and default state', () => {
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      expect(result.current.messages).toEqual([])
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(result.current.suggestions).toEqual([])
    })
  })

  describe('Send Message', () => {
    it('should successfully send message and receive AI response', async () => {
      mockApiCall(mockAxios.post, mockApiResponses.aiResponse)
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      await act(async () => {
        await result.current.sendMessage('Hello CapeAI!')
      })
      
      expect(result.current.messages).toHaveLength(2) // User message + AI response
      expect(result.current.messages[0]).toMatchObject({
        text: 'Hello CapeAI!',
        sender: 'user'
      })
      expect(result.current.messages[1]).toMatchObject({
        text: mockApiResponses.aiResponse.response,
        sender: 'ai'
      })
      expect(result.current.error).toBeNull()
    })

    it('should handle API errors gracefully', async () => {
      const errorMessage = 'AI service unavailable'
      mockAxios.post.mockRejectedValue({
        response: { data: { detail: errorMessage } }
      })
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      await act(async () => {
        await result.current.sendMessage('Hello CapeAI!')
      })
      
      expect(result.current.error).toBe(errorMessage)
      expect(result.current.messages).toHaveLength(1) // Only user message
    })

    it('should set loading state during message sending', async () => {
      let resolveMessage
      mockAxios.post.mockReturnValue(new Promise(resolve => {
        resolveMessage = resolve
      }))
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      act(() => {
        result.current.sendMessage('Hello CapeAI!')
      })
      
      expect(result.current.isLoading).toBe(true)
      
      await act(async () => {
        resolveMessage({ data: mockApiResponses.aiResponse })
      })
      
      expect(result.current.isLoading).toBe(false)
    })

    it('should include context information in API request', async () => {
      mockApiCall(mockAxios.post, mockApiResponses.aiResponse)
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      const context = {
        page: '/dashboard',
        user_intent: 'testing'
      }
      
      await act(async () => {
        await result.current.sendMessage('Hello!', context)
      })
      
      expect(mockAxios.post).toHaveBeenCalledWith(
        '/api/ai/prompt',
        expect.objectContaining({
          message: 'Hello!',
          context: context
        }),
        expect.any(Object)
      )
    })
  })

  describe('Clear Messages', () => {
    it('should clear all messages and reset state', async () => {
      mockApiCall(mockAxios.post, mockApiResponses.aiResponse)
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      // Add some messages first
      await act(async () => {
        await result.current.sendMessage('Test message')
      })
      
      expect(result.current.messages).toHaveLength(2)
      
      act(() => {
        result.current.clearMessages()
      })
      
      expect(result.current.messages).toEqual([])
      expect(result.current.error).toBeNull()
    })
  })

  describe('Get Suggestions', () => {
    it('should fetch AI suggestions successfully', async () => {
      mockApiCall(mockAxios.get, mockApiResponses.suggestions)
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      await act(async () => {
        await result.current.getSuggestions('dashboard', 'beginner')
      })
      
      expect(result.current.suggestions).toEqual(mockApiResponses.suggestions.suggestions)
      expect(mockAxios.get).toHaveBeenCalledWith(
        '/api/ai/suggestions',
        expect.objectContaining({
          params: {
            context: 'dashboard',
            user_level: 'beginner'
          }
        })
      )
    })

    it('should handle suggestions API errors', async () => {
      const errorMessage = 'Failed to fetch suggestions'
      mockAxios.get.mockRejectedValue({
        response: { data: { detail: errorMessage } }
      })
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      await act(async () => {
        await result.current.getSuggestions()
      })
      
      expect(result.current.error).toBe(errorMessage)
      expect(result.current.suggestions).toEqual([])
    })
  })

  describe('Message History Management', () => {
    it('should maintain conversation history in order', async () => {
      mockApiCall(mockAxios.post, mockApiResponses.aiResponse)
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      await act(async () => {
        await result.current.sendMessage('First message')
      })
      
      await act(async () => {
        await result.current.sendMessage('Second message')
      })
      
      expect(result.current.messages).toHaveLength(4) // 2 user + 2 AI messages
      expect(result.current.messages[0].text).toBe('First message')
      expect(result.current.messages[2].text).toBe('Second message')
    })

    it('should handle empty or whitespace messages', async () => {
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      await act(async () => {
        await result.current.sendMessage('   ')
      })
      
      expect(result.current.messages).toEqual([])
      expect(mockAxios.post).not.toHaveBeenCalled()
    })
  })

  describe('Authentication Integration', () => {
    it('should include authentication headers in requests', async () => {
      mockApiCall(mockAxios.post, mockApiResponses.aiResponse)
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      await act(async () => {
        await result.current.sendMessage('Authenticated message')
      })
      
      expect(mockAxios.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(Object),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${mockAuthContext.token}`
          })
        })
      )
    })

    it('should handle authentication errors', async () => {
      mockAxios.post.mockRejectedValue({
        response: { status: 401, data: { detail: 'Unauthorized' } }
      })
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      await act(async () => {
        await result.current.sendMessage('Test message')
      })
      
      expect(result.current.error).toBe('Unauthorized')
    })
  })

  describe('Error Recovery', () => {
    it('should clear errors on successful operations', async () => {
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      // First, cause an error
      mockAxios.post.mockRejectedValue({
        response: { data: { detail: 'Network error' } }
      })
      
      await act(async () => {
        await result.current.sendMessage('Error message')
      })
      
      expect(result.current.error).toBe('Network error')
      
      // Then, make a successful request
      mockApiCall(mockAxios.post, mockApiResponses.aiResponse)
      
      await act(async () => {
        await result.current.sendMessage('Success message')
      })
      
      expect(result.current.error).toBeNull()
    })
  })

  describe('Message Formatting', () => {
    it('should properly format messages with timestamps', async () => {
      mockApiCall(mockAxios.post, mockApiResponses.aiResponse)
      
      const { result } = renderHook(() => useCapeAI(), { wrapper })
      
      const beforeTime = Date.now()
      
      await act(async () => {
        await result.current.sendMessage('Timestamped message')
      })
      
      const afterTime = Date.now()
      
      const userMessage = result.current.messages[0]
      expect(userMessage).toHaveProperty('timestamp')
      expect(userMessage).toHaveProperty('id')
      
      const messageTime = new Date(userMessage.timestamp).getTime()
      expect(messageTime).toBeGreaterThanOrEqual(beforeTime)
      expect(messageTime).toBeLessThanOrEqual(afterTime)
    })
  })
})
