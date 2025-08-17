/**
 * Advanced Conversation Management Interface
 * React components for intelligent conversation threading and organization
 * 
 * Author: CapeAI Development Team
 * Date: July 25, 2025
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  MessageSquare, 
  Search, 
  Filter, 
  Plus, 
  Settings, 
  Archive, 
  Share2, 
  Edit3, 
  Trash2, 
  GitBranch, 
  BarChart3, 
  Clock, 
  Users, 
  Tag, 
  Thread,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  Download,
  Upload,
  RefreshCw,
  Zap,
  Brain,
  Target,
  Hash,
  Calendar,
  TrendingUp,
  Activity,
  MessageCircle,
  Layers,
  BookOpen,
  Lightbulb
} from 'lucide-react';

// Main conversation management interface
const ConversationManager = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    type: '',
    dateRange: '',
    tags: []
  });
  const [viewMode, setViewMode] = useState('list'); // list, grid, timeline
  const [activeTab, setActiveTab] = useState('conversations');
  const [showFilters, setShowFilters] = useState(false);

  // Load conversations on component mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/conversations?user_id=current_user');
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      } else {
        throw new Error('Failed to load conversations');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const searchConversations = async (query) => {
    if (!query.trim()) {
      loadConversations();
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/conversations/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
          filters: filters 
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredConversations = useMemo(() => {
    let filtered = conversations;

    if (filters.status) {
      filtered = filtered.filter(conv => conv.status === filters.status);
    }
    if (filters.type) {
      filtered = filtered.filter(conv => conv.conversation_type === filters.type);
    }
    if (filters.tags.length > 0) {
      filtered = filtered.filter(conv => 
        filters.tags.some(tag => conv.tags.includes(tag))
      );
    }

    return filtered;
  }, [conversations, filters]);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <ConversationSidebar
          conversations={filteredConversations}
          selectedConversation={selectedConversation}
          onSelectConversation={setSelectedConversation}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearch={searchConversations}
          filters={filters}
          onFiltersChange={setFilters}
          showFilters={showFilters}
          onToggleFilters={setShowFilters}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          loading={loading}
        />
      </div>

      {/* Main content area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <ConversationDetail
            conversation={selectedConversation}
            onUpdateConversation={setSelectedConversation}
            onDeleteConversation={() => {
              setSelectedConversation(null);
              loadConversations();
            }}
          />
        ) : (
          <ConversationDashboard
            conversations={conversations}
            onSelectConversation={setSelectedConversation}
            onRefresh={loadConversations}
          />
        )}
      </div>
    </div>
  );
};

// Sidebar component for conversation list and filters
const ConversationSidebar = ({
  conversations,
  selectedConversation,
  onSelectConversation,
  searchQuery,
  onSearchChange,
  onSearch,
  filters,
  onFiltersChange,
  showFilters,
  onToggleFilters,
  viewMode,
  onViewModeChange,
  loading
}) => {
  const [newConversationModal, setNewConversationModal] = useState(false);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Conversations</h2>
          <button
            onClick={() => setNewConversationModal(true)}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
            title="New Conversation"
          >
            <Plus className="h-5 w-5" />
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && onSearch(searchQuery)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filter toggle */}
        <div className="flex items-center justify-between">
          <button
            onClick={onToggleFilters}
            className="flex items-center text-sm text-gray-600 hover:text-gray-900"
          >
            <Filter className="h-4 w-4 mr-1" />
            Filters
            {showFilters ? <ChevronDown className="h-4 w-4 ml-1" /> : <ChevronRight className="h-4 w-4 ml-1" />}
          </button>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={() => onViewModeChange('list')}
              className={`p-1 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
            >
              <Layers className="h-4 w-4" />
            </button>
            <button
              onClick={() => onViewModeChange('grid')}
              className={`p-1 rounded ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-400'}`}
            >
              <Hash className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <ConversationFilters
            filters={filters}
            onFiltersChange={onFiltersChange}
          />
        )}
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-center text-gray-500">
            <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
            Loading conversations...
          </div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <MessageSquare className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No conversations found</p>
            <p className="text-sm mt-1">Create your first conversation to get started</p>
          </div>
        ) : (
          <ConversationList
            conversations={conversations}
            selectedConversation={selectedConversation}
            onSelectConversation={onSelectConversation}
            viewMode={viewMode}
          />
        )}
      </div>

      {/* New conversation modal */}
      {newConversationModal && (
        <NewConversationModal
          onClose={() => setNewConversationModal(false)}
          onCreated={(conversation) => {
            setNewConversationModal(false);
            onSelectConversation(conversation);
          }}
        />
      )}
    </div>
  );
};

// Filters component
const ConversationFilters = ({ filters, onFiltersChange }) => {
  const conversationTypes = [
    'general', 'question_answer', 'brainstorming', 'problem_solving',
    'learning', 'creative', 'technical', 'research', 'planning', 'discussion'
  ];

  const conversationStatuses = ['active', 'paused', 'completed', 'archived'];

  return (
    <div className="mt-3 space-y-3 p-3 bg-gray-50 rounded-lg">
      {/* Status filter */}
      <div>
        <label className="block text-xs font-medium text-gray-700 mb-1">Status</label>
        <select
          value={filters.status}
          onChange={(e) => onFiltersChange({ ...filters, status: e.target.value })}
          className="w-full text-sm border border-gray-300 rounded px-2 py-1"
        >
          <option value="">All statuses</option>
          {conversationStatuses.map(status => (
            <option key={status} value={status}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Type filter */}
      <div>
        <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
        <select
          value={filters.type}
          onChange={(e) => onFiltersChange({ ...filters, type: e.target.value })}
          className="w-full text-sm border border-gray-300 rounded px-2 py-1"
        >
          <option value="">All types</option>
          {conversationTypes.map(type => (
            <option key={type} value={type}>
              {type.replace('_', ' ').charAt(0).toUpperCase() + type.replace('_', ' ').slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Date range filter */}
      <div>
        <label className="block text-xs font-medium text-gray-700 mb-1">Date Range</label>
        <select
          value={filters.dateRange}
          onChange={(e) => onFiltersChange({ ...filters, dateRange: e.target.value })}
          className="w-full text-sm border border-gray-300 rounded px-2 py-1"
        >
          <option value="">All time</option>
          <option value="today">Today</option>
          <option value="week">This week</option>
          <option value="month">This month</option>
          <option value="quarter">This quarter</option>
        </select>
      </div>
    </div>
  );
};

// Conversation list component
const ConversationList = ({ conversations, selectedConversation, onSelectConversation, viewMode }) => {
  if (viewMode === 'grid') {
    return (
      <div className="p-4 grid grid-cols-1 gap-3">
        {conversations.map(conversation => (
          <ConversationGridItem
            key={conversation.conversation_id}
            conversation={conversation}
            isSelected={selectedConversation?.conversation_id === conversation.conversation_id}
            onSelect={onSelectConversation}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {conversations.map(conversation => (
        <ConversationListItem
          key={conversation.conversation_id}
          conversation={conversation}
          isSelected={selectedConversation?.conversation_id === conversation.conversation_id}
          onSelect={onSelectConversation}
        />
      ))}
    </div>
  );
};

// Individual conversation list item
const ConversationListItem = ({ conversation, isSelected, onSelect }) => {
  const getStatusColor = (status) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      paused: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-blue-100 text-blue-800',
      archived: 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getTypeIcon = (type) => {
    const icons = {
      general: MessageSquare,
      question_answer: Lightbulb,
      brainstorming: Brain,
      problem_solving: Target,
      learning: BookOpen,
      creative: Zap,
      technical: Settings,
      research: Search,
      planning: Calendar,
      discussion: Users
    };
    const Icon = icons[type] || MessageSquare;
    return <Icon className="h-4 w-4" />;
  };

  return (
    <button
      onClick={() => onSelect(conversation)}
      className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
        isSelected ? 'bg-blue-50 border-r-2 border-blue-500' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center space-x-2">
          <div className="text-gray-500">
            {getTypeIcon(conversation.conversation_type)}
          </div>
          <h3 className="font-medium text-gray-900 text-sm line-clamp-1">
            {conversation.title}
          </h3>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(conversation.status)}`}>
          {conversation.status}
        </span>
      </div>

      <p className="text-xs text-gray-600 mb-2 line-clamp-2">
        {conversation.description || 'No description'}
      </p>

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-3">
          <span className="flex items-center">
            <MessageCircle className="h-3 w-3 mr-1" />
            {conversation.message_count}
          </span>
          <span className="flex items-center">
            <Thread className="h-3 w-3 mr-1" />
            {conversation.thread_count}
          </span>
        </div>
        <span>{new Date(conversation.updated_at).toLocaleDateString()}</span>
      </div>

      {conversation.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {conversation.tags.slice(0, 3).map(tag => (
            <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
              {tag}
            </span>
          ))}
          {conversation.tags.length > 3 && (
            <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
              +{conversation.tags.length - 3}
            </span>
          )}
        </div>
      )}
    </button>
  );
};

// Grid view item
const ConversationGridItem = ({ conversation, isSelected, onSelect }) => {
  const getStatusColor = (status) => {
    const colors = {
      active: 'border-green-500 bg-green-50',
      paused: 'border-yellow-500 bg-yellow-50',
      completed: 'border-blue-500 bg-blue-50',
      archived: 'border-gray-500 bg-gray-50'
    };
    return colors[status] || 'border-gray-500 bg-gray-50';
  };

  return (
    <button
      onClick={() => onSelect(conversation)}
      className={`p-4 rounded-lg border-2 text-left hover:shadow-md transition-all ${
        isSelected ? 'border-blue-500 bg-blue-50' : getStatusColor(conversation.status)
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-medium text-gray-900 text-sm line-clamp-1">
          {conversation.title}
        </h3>
        <span className="text-xs text-gray-500">
          {conversation.conversation_type.replace('_', ' ')}
        </span>
      </div>

      <p className="text-xs text-gray-600 mb-3 line-clamp-2">
        {conversation.description || 'No description'}
      </p>

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-2">
          <span>{conversation.message_count} msgs</span>
          <span>{conversation.thread_count} threads</span>
        </div>
        <span>{new Date(conversation.updated_at).toLocaleDateString()}</span>
      </div>
    </button>
  );
};

// Conversation detail view
const ConversationDetail = ({ conversation, onUpdateConversation, onDeleteConversation }) => {
  const [activeTab, setActiveTab] = useState('messages');
  const [messages, setMessages] = useState([]);
  const [threads, setThreads] = useState([]);
  const [summary, setSummary] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (conversation) {
      loadConversationData();
    }
  }, [conversation]);

  const loadConversationData = async () => {
    setLoading(true);
    try {
      // Load messages
      const messagesResponse = await fetch(`/api/conversations/${conversation.conversation_id}/messages`);
      if (messagesResponse.ok) {
        const messagesData = await messagesResponse.json();
        setMessages(messagesData);
      }

      // Load threads
      const threadsResponse = await fetch(`/api/conversations/${conversation.conversation_id}/threads`);
      if (threadsResponse.ok) {
        const threadsData = await threadsResponse.json();
        setThreads(threadsData);
      }
    } catch (err) {
      console.error('Failed to load conversation data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const response = await fetch(`/api/conversations/${conversation.conversation_id}/summary`);
      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await fetch(`/api/conversations/${conversation.conversation_id}/analytics`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  };

  const tabs = [
    { id: 'messages', label: 'Messages', icon: MessageCircle },
    { id: 'threads', label: 'Threads', icon: Thread },
    { id: 'summary', label: 'Summary', icon: BookOpen },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 }
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">{conversation.title}</h1>
            <p className="text-sm text-gray-600 mt-1">{conversation.description}</p>
            <div className="flex items-center space-x-4 mt-2">
              <span className="flex items-center text-xs text-gray-500">
                <MessageCircle className="h-3 w-3 mr-1" />
                {conversation.message_count} messages
              </span>
              <span className="flex items-center text-xs text-gray-500">
                <Thread className="h-3 w-3 mr-1" />
                {conversation.thread_count} threads
              </span>
              <span className="flex items-center text-xs text-gray-500">
                <Clock className="h-3 w-3 mr-1" />
                Updated {new Date(conversation.updated_at).toLocaleDateString()}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg">
              <Share2 className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg">
              <Download className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-6 mt-4">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  if (tab.id === 'summary' && !summary) loadSummary();
                  if (tab.id === 'analytics' && !analytics) loadAnalytics();
                }}
                className={`flex items-center space-x-2 pb-2 border-b-2 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'messages' && (
          <ConversationMessages
            conversationId={conversation.conversation_id}
            messages={messages}
            threads={threads}
            onRefresh={loadConversationData}
          />
        )}
        {activeTab === 'threads' && (
          <ConversationThreads
            conversationId={conversation.conversation_id}
            threads={threads}
            onRefresh={loadConversationData}
          />
        )}
        {activeTab === 'summary' && (
          <ConversationSummary
            conversationId={conversation.conversation_id}
            summary={summary}
            onRefresh={loadSummary}
          />
        )}
        {activeTab === 'analytics' && (
          <ConversationAnalytics
            conversationId={conversation.conversation_id}
            analytics={analytics}
            onRefresh={loadAnalytics}
          />
        )}
      </div>
    </div>
  );
};

// Messages view component
const ConversationMessages = ({ conversationId, messages, threads, onRefresh }) => {
  const [selectedThread, setSelectedThread] = useState(null);
  const [showThreadView, setShowThreadView] = useState(false);

  const filteredMessages = selectedThread
    ? messages.filter(msg => msg.thread_id === selectedThread)
    : messages;

  const getRoleColor = (role) => {
    const colors = {
      user: 'bg-blue-100 text-blue-800',
      assistant: 'bg-green-100 text-green-800',
      system: 'bg-gray-100 text-gray-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="flex h-full">
      {/* Thread sidebar */}
      <div className="w-64 bg-gray-50 border-r border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium text-gray-900">Threads</h3>
          <button
            onClick={() => setShowThreadView(!showThreadView)}
            className="p-1 text-gray-500 hover:text-gray-700"
          >
            {showThreadView ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>

        <button
          onClick={() => setSelectedThread(null)}
          className={`w-full text-left p-2 rounded mb-2 text-sm ${
            !selectedThread ? 'bg-blue-100 text-blue-800' : 'hover:bg-gray-100'
          }`}
        >
          All Messages ({messages.length})
        </button>

        {threads.map(thread => (
          <button
            key={thread.thread_id}
            onClick={() => setSelectedThread(thread.thread_id)}
            className={`w-full text-left p-2 rounded mb-2 text-sm ${
              selectedThread === thread.thread_id ? 'bg-blue-100 text-blue-800' : 'hover:bg-gray-100'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="line-clamp-1">{thread.title}</span>
              <span className="text-xs text-gray-500">({thread.message_count})</span>
            </div>
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredMessages.length === 0 ? (
          <div className="text-center text-gray-500 mt-12">
            <MessageSquare className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No messages in this conversation</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredMessages.map(message => (
              <div key={message.message_id} className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(message.role)}`}>
                      {message.role}
                    </span>
                    {message.thread_id && (
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs">
                        Thread
                      </span>
                    )}
                    {message.edited && (
                      <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs">
                        Edited
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(message.timestamp).toLocaleString()}
                  </span>
                </div>
                <p className="text-gray-900 whitespace-pre-wrap">{message.content}</p>
                <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                  <span>{message.tokens} tokens</span>
                  <div className="flex items-center space-x-2">
                    <button className="hover:text-gray-700">
                      <Edit3 className="h-3 w-3" />
                    </button>
                    <button className="hover:text-red-600">
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Threads view component
const ConversationThreads = ({ conversationId, threads, onRefresh }) => {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900">Conversation Threads</h3>
        <p className="text-sm text-gray-600 mt-1">
          Organize your conversation with intelligent threading
        </p>
      </div>

      {threads.length === 0 ? (
        <div className="text-center text-gray-500 mt-12">
          <Thread className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p>No threads created yet</p>
          <p className="text-sm mt-1">Threads will be created automatically as the conversation grows</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {threads.map(thread => (
            <div key={thread.thread_id} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900 line-clamp-1">{thread.title}</h4>
                <span className="text-xs text-gray-500">{thread.message_count} msgs</span>
              </div>
              
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {thread.description || 'No description'}
              </p>

              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                <span>Type: {thread.thread_type}</span>
                <span>Status: {thread.status}</span>
              </div>

              {thread.topic_keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {thread.topic_keywords.slice(0, 3).map(keyword => (
                    <span key={keyword} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                      {keyword}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {new Date(thread.updated_at).toLocaleDateString()}
                </span>
                <div className="flex items-center space-x-1">
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <Edit3 className="h-3 w-3" />
                  </button>
                  <button className="p-1 text-gray-400 hover:text-red-600">
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Summary view component
const ConversationSummary = ({ conversationId, summary, onRefresh }) => {
  if (!summary) {
    return (
      <div className="p-6">
        <div className="text-center">
          <button
            onClick={onRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Generate Summary
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl">
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">{summary.title}</h3>
        
        <div className="space-y-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Brief Summary</h4>
            <p className="text-gray-700">{summary.brief_summary}</p>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-2">Detailed Summary</h4>
            <p className="text-gray-700">{summary.detailed_summary}</p>
          </div>

          {summary.key_points.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Key Points</h4>
              <ul className="list-disc list-inside space-y-1">
                {summary.key_points.map((point, index) => (
                  <li key={index} className="text-gray-700">{point}</li>
                ))}
              </ul>
            </div>
          )}

          {summary.topics_discussed.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Topics Discussed</h4>
              <div className="flex flex-wrap gap-2">
                {summary.topics_discussed.map(topic => (
                  <span key={topic} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Sentiment Analysis</h4>
              <div className="space-y-2">
                {Object.entries(summary.sentiment_analysis).map(([sentiment, score]) => (
                  <div key={sentiment} className="flex items-center justify-between">
                    <span className="capitalize text-gray-700">{sentiment}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            sentiment === 'positive' ? 'bg-green-500' :
                            sentiment === 'negative' ? 'bg-red-500' : 'bg-gray-500'
                          }`}
                          style={{ width: `${score * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">{Math.round(score * 100)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Quality Score</h4>
              <div className="flex items-center">
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className="h-4 bg-blue-500 rounded-full"
                    style={{ width: `${summary.quality_score * 100}%` }}
                  />
                </div>
                <span className="ml-3 text-sm font-medium text-gray-900">
                  {Math.round(summary.quality_score * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Analytics view component
const ConversationAnalytics = ({ conversationId, analytics, onRefresh }) => {
  if (!analytics) {
    return (
      <div className="p-6">
        <div className="text-center">
          <button
            onClick={onRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Generate Analytics
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <MessageCircle className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Messages</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.message_count}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Tokens</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.total_tokens.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.avg_response_time.toFixed(2)}s</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Engagement</p>
              <p className="text-2xl font-bold text-gray-900">{Math.round(analytics.engagement_score * 100)}%</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="font-medium text-gray-900 mb-4">Topic Distribution</h4>
          <div className="space-y-3">
            {Object.entries(analytics.topic_distribution).slice(0, 8).map(([topic, percentage]) => (
              <div key={topic} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 capitalize">{topic}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 bg-blue-500 rounded-full"
                      style={{ width: `${percentage * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600 w-10 text-right">
                    {Math.round(percentage * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="font-medium text-gray-900 mb-4">User Participation</h4>
          <div className="space-y-4">
            {Object.entries(analytics.user_participation).map(([role, data]) => (
              <div key={role} className="border-b border-gray-100 pb-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 capitalize">{role}</span>
                  <span className="text-sm text-gray-600">{data.message_count} messages</span>
                </div>
                <div className="text-sm text-gray-600">
                  {data.token_count.toLocaleString()} tokens
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="font-medium text-gray-900 mb-4">Peak Activity Times</h4>
          <div className="space-y-2">
            {analytics.peak_activity_times.map((time, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{time}</span>
                <span className="text-sm text-gray-600">Peak #{index + 1}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h4 className="font-medium text-gray-900 mb-4">Quality Metrics</h4>
          <div className="space-y-3">
            {Object.entries(analytics.quality_metrics).map(([metric, score]) => (
              <div key={metric} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 capitalize">{metric}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 bg-green-500 rounded-full"
                      style={{ width: `${score * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600">{Math.round(score * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard overview component
const ConversationDashboard = ({ conversations, onSelectConversation, onRefresh }) => {
  const stats = useMemo(() => {
    const totalMessages = conversations.reduce((sum, conv) => sum + conv.message_count, 0);
    const totalThreads = conversations.reduce((sum, conv) => sum + conv.thread_count, 0);
    const activeConversations = conversations.filter(conv => conv.status === 'active').length;
    
    const typeDistribution = {};
    conversations.forEach(conv => {
      typeDistribution[conv.conversation_type] = (typeDistribution[conv.conversation_type] || 0) + 1;
    });

    return {
      totalConversations: conversations.length,
      totalMessages,
      totalThreads,
      activeConversations,
      typeDistribution
    };
  }, [conversations]);

  return (
    <div className="p-6">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Conversation Dashboard</h2>
          <button
            onClick={onRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>
        </div>
        <p className="text-gray-600 mt-1">Overview of your conversation activity and insights</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <MessageSquare className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Conversations</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalConversations}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Conversations</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activeConversations}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <MessageCircle className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Messages</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalMessages}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <Thread className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Threads</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalThreads}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent conversations */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Conversations</h3>
        <div className="space-y-3">
          {conversations.slice(0, 5).map(conversation => (
            <button
              key={conversation.conversation_id}
              onClick={() => onSelectConversation(conversation)}
              className="w-full flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg text-left"
            >
              <div>
                <h4 className="font-medium text-gray-900">{conversation.title}</h4>
                <p className="text-sm text-gray-600">
                  {conversation.message_count} messages • {conversation.thread_count} threads
                </p>
              </div>
              <div className="text-right">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  conversation.status === 'active' ? 'bg-green-100 text-green-800' :
                  conversation.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {conversation.status}
                </span>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(conversation.updated_at).toLocaleDateString()}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// New conversation modal
const NewConversationModal = ({ onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    conversation_type: 'general',
    tags: '',
    auto_threading: true,
    threading_strategy: 'hybrid'
  });
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCreating(true);

    try {
      const requestData = {
        ...formData,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };

      const response = await fetch('/api/conversations?user_id=current_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const conversation = await response.json();
        onCreated(conversation);
      } else {
        throw new Error('Failed to create conversation');
      }
    } catch (err) {
      console.error('Failed to create conversation:', err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-medium text-gray-900 mb-4">New Conversation</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter conversation title"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              placeholder="Optional description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={formData.conversation_type}
              onChange={(e) => setFormData({ ...formData, conversation_type: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="general">General</option>
              <option value="question_answer">Q&A</option>
              <option value="brainstorming">Brainstorming</option>
              <option value="problem_solving">Problem Solving</option>
              <option value="learning">Learning</option>
              <option value="creative">Creative</option>
              <option value="technical">Technical</option>
              <option value="research">Research</option>
              <option value="planning">Planning</option>
              <option value="discussion">Discussion</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter tags separated by commas"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="auto_threading"
              checked={formData.auto_threading}
              onChange={(e) => setFormData({ ...formData, auto_threading: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="auto_threading" className="ml-2 text-sm text-gray-700">
              Enable automatic threading
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {creating ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ConversationManager;
