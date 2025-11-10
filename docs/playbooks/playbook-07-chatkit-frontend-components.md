# Playbook 07: ChatKit Frontend Components

**Owner**: Codex
**Supporting Agents**: CapeAI, TestGuardian
**Status**: Doing
**Priority**: P1

## 1) Outcome

**Definition of Done:**
- React components for chat interface integrated with backend ChatKit API
- Real-time messaging with WebSocket support
- Thread management UI with context preservation
- Chat event display with role-based styling (user, assistant, system)
- TypeScript interfaces matching backend models

**KPIs:**
- Chat component renders messages < 100ms
- WebSocket connection established < 2s
- Test coverage > 85% for chat components
- Responsive design works on mobile/desktop

## 2) Scope (In / Out)

**In:**
- React ChatThread component with message history
- React ChatInput component with send functionality
- WebSocket client for real-time updates
- TypeScript types for chat models (thread, events)
- Message rendering with tool output support
- Thread context management and placement routing

**Out:**
- Agent marketplace UI (separate playbook)
- Payment integration within chat
- Advanced chat formatting (markdown, code blocks)
- File upload/sharing in chat

## 3) Dependencies

**Upstream:**
- CHAT-001: ChatKit backend integration ✅ Complete
- Database schema for app_chat_threads and app_chat_events ✅ Complete
- Authentication system for user context ✅ Complete

**Downstream:**
- CHAT-005: Agent marketplace UI
- CHAT-007: Onboarding flow integration

## 4) Milestones

### M1 – Basic Chat UI (Week 1)

- ChatThread component displays message history
- ChatInput component sends messages to API
- Basic TypeScript types defined

### M2 – Real-time Features (Week 2)

- WebSocket connection for live updates
- Message status indicators (sending, sent, error)
- Thread switching without page reload

### M3 – Polish & Testing (Week 3)

- Responsive design implementation
- Comprehensive test suite
- Error handling and loading states

## 5) Checklist (Executable)

**Frontend Development:**
- [✅] Create `client/src/components/chat/` directory structure
- [✅] Implement `ChatThread.tsx` component
- [✅] Implement `ChatInput.tsx` component
- [✅] Implement `MessageList.tsx` component
- [✅] Create TypeScript types in `client/types/chat.ts`
- [✅] Add WebSocket client in `client/src/services/websocket.ts`
- [✅] Integrate with React Router for thread routing
- [ ] Add chat CSS/Tailwind styles enhancement
- [ ] Enhance real-time WebSocket integration

**API Integration:**
- [ ] Create chat API client functions
- [ ] Implement error handling for API calls
- [ ] Add loading states and optimistic updates
- [ ] Test against backend ChatKit endpoints

**Testing & Quality:**
- [ ] Write unit tests for chat components
- [ ] Write integration tests for chat flow
- [ ] Test WebSocket connection handling
- [ ] Validate responsive design
- [ ] Run accessibility audit on chat UI

**Make Targets:**
- [ ] `make test-frontend` passes all chat tests
- [ ] `make lint-frontend` passes without errors
- [ ] `make build-frontend` includes chat components
- [ ] `make docker-build` includes updated frontend

## 6) Runbook / Commands

```bash
# Development setup
cd client
npm install
npm run dev

# Create component structure
mkdir -p src/components/chat
mkdir -p src/types
mkdir -p src/services

# Run tests specifically for chat
npm test -- --testPathPattern=chat

# Build and validate
npm run build
npm run type-check

# Backend API testing
make codex-test  # Run backend tests
curl -X GET http://localhost:8000/api/chat/threads

# Full integration test
make docker-build
make docker-run
# Test chat functionality at http://localhost:5173
```

## 7) Implementation Notes

**Key Files to Create/Modify:**
- `client/src/components/chat/ChatThread.tsx`
- `client/src/components/chat/ChatInput.tsx`
- `client/src/components/chat/MessageList.tsx`
- `client/src/components/chat/Message.tsx`
- `client/types/chat.ts`
- `client/src/services/chatApi.ts`
- `client/src/hooks/useWebSocket.ts`

**Backend API Endpoints to Integrate:**
- `GET /api/chat/threads` - List user's chat threads
- `POST /api/chat/threads` - Create new thread
- `GET /api/chat/threads/{thread_id}/events` - Get thread messages
- `POST /api/chat/threads/{thread_id}/events` - Send message
- WebSocket endpoint for real-time updates

**Testing Strategy:**
- Mock WebSocket connections for unit tests
- Use React Testing Library for component tests
- Mock API responses with MSW (Mock Service Worker)
- End-to-end tests with Playwright (future enhancement)
