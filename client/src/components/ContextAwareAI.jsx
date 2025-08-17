import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  MessageSquare, 
  Brain, 
  User, 
  Settings, 
  BarChart3, 
  Zap,
  Clock,
  Target,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Send,
  History,
  Lightbulb,
  Filter,
  Eye,
  Share2
} from 'lucide-react';

const ContextAwareAI = () => {
  // State management
  const [query, setQuery] = useState('');
  const [userProfile, setUserProfile] = useState({
    user_id: 'demo-user',
    communication_style: 'balanced',
    learning_style: 'mixed',
    expertise_level: 'intermediate',
    interests: ['technology', 'programming']
  });
  const [conversationHistory, setConversationHistory] = useState([]);
  const [currentResponse, setCurrentResponse] = useState(null);
  const [contextAnalysis, setContextAnalysis] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [contextTypes, setContextTypes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [simulationResults, setSimulationResults] = useState([]);

  // Load initial data
  useEffect(() => {
    loadStrategies();
    loadContextTypes();
    loadPerformanceMetrics();
  }, []);

  // Load available strategies
  const loadStrategies = async () => {
    try {
      const response = await fetch('/api/v1/context-ai/strategies');
      if (response.ok) {
        const data = await response.json();
        setStrategies(data);
      }
    } catch (err) {
      console.error('Failed to load strategies:', err);
    }
  };

  // Load context types
  const loadContextTypes = async () => {
    try {
      const response = await fetch('/api/v1/context-ai/context-types');
      if (response.ok) {
        const data = await response.json();
        setContextTypes(data);
      }
    } catch (err) {
      console.error('Failed to load context types:', err);
    }
  };

  // Load performance metrics
  const loadPerformanceMetrics = async () => {
    try {
      const response = await fetch('/api/v1/context-ai/performance-metrics');
      if (response.ok) {
        const data = await response.json();
        setPerformanceMetrics(data);
      }
    } catch (err) {
      console.error('Failed to load performance metrics:', err);
    }
  };

  // Generate context-aware response
  const generateResponse = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/context-ai/generate-response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          user_profile: userProfile,
          conversation_history: conversationHistory,
          additional_context: null
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setCurrentResponse(data);

      // Add to conversation history
      const newUserMessage = {
        role: 'user',
        content: query,
        timestamp: new Date().toISOString()
      };

      const newAIMessage = {
        role: 'assistant',
        content: data.prompt,
        timestamp: new Date().toISOString(),
        metadata: { strategy: data.strategy }
      };

      setConversationHistory(prev => [...prev, newUserMessage, newAIMessage]);
      setQuery('');

      // Refresh metrics
      loadPerformanceMetrics();

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Analyze conversation context
  const analyzeContext = async () => {
    if (conversationHistory.length === 0) {
      setError('No conversation history to analyze');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/context-ai/analyze-context', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userProfile.user_id,
          conversation_history: conversationHistory
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setContextAnalysis(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate conversation flow
  const simulateConversation = async () => {
    const sampleQueries = [
      "What is machine learning?",
      "How do neural networks work?",
      "Can you explain deep learning?",
      "What are the applications of AI?",
      "How do I get started with Python?"
    ];

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/context-ai/simulate-conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_profile: userProfile,
          queries: sampleQueries,
          max_queries: 5
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSimulationResults(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear cache
  const clearCache = async () => {
    try {
      const response = await fetch('/api/v1/context-ai/clear-cache', {
        method: 'POST'
      });

      if (response.ok) {
        loadPerformanceMetrics();
        alert('Cache cleared successfully');
      }
    } catch (err) {
      setError('Failed to clear cache');
    }
  };

  // Update user profile
  const updateUserProfile = useCallback((field, value) => {
    setUserProfile(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Memoized components
  const UserProfileEditor = useMemo(() => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center">
        <User className="mr-2" size={20} />
        User Profile
      </h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Communication Style
          </label>
          <select
            value={userProfile.communication_style}
            onChange={(e) => updateUserProfile('communication_style', e.target.value)}
            className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="balanced">Balanced</option>
            <option value="direct">Direct</option>
            <option value="friendly">Friendly</option>
            <option value="professional">Professional</option>
            <option value="casual">Casual</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Learning Style
          </label>
          <select
            value={userProfile.learning_style}
            onChange={(e) => updateUserProfile('learning_style', e.target.value)}
            className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="mixed">Mixed</option>
            <option value="visual">Visual</option>
            <option value="auditory">Auditory</option>
            <option value="hands-on">Hands-on</option>
            <option value="reading">Reading</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Expertise Level
          </label>
          <select
            value={userProfile.expertise_level}
            onChange={(e) => updateUserProfile('expertise_level', e.target.value)}
            className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="expert">Expert</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Interests (comma-separated)
          </label>
          <input
            type="text"
            value={userProfile.interests.join(', ')}
            onChange={(e) => updateUserProfile('interests', e.target.value.split(',').map(s => s.trim()))}
            className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="technology, programming, AI, etc."
          />
        </div>
      </div>
    </div>
  ), [userProfile, updateUserProfile]);

  const ChatInterface = useMemo(() => (
    <div className="space-y-6">
      {/* Query Input */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <MessageSquare className="mr-2" size={20} />
          Context-Aware Chat
        </h2>
        
        <div className="flex space-x-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && generateResponse()}
            placeholder="Ask me anything..."
            className="flex-1 p-3 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={generateResponse}
            disabled={isLoading || !query.trim()}
            className="px-6 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isLoading ? <RefreshCw className="animate-spin" size={16} /> : <Send size={16} />}
          </button>
        </div>
      </div>

      {/* Current Response */}
      {currentResponse && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Brain className="mr-2" size={18} />
            Generated Response
          </h3>
          
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-md">
              <p className="text-gray-800">{currentResponse.prompt}</p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="font-medium">Strategy:</span>
                <p className="text-blue-600">{currentResponse.strategy}</p>
              </div>
              <div>
                <span className="font-medium">Confidence:</span>
                <p className="text-green-600">{(currentResponse.confidence_score * 100).toFixed(1)}%</p>
              </div>
              <div>
                <span className="font-medium">Processing:</span>
                <p className="text-purple-600">{currentResponse.processing_time_ms.toFixed(1)}ms</p>
              </div>
              <div>
                <span className="font-medium">Cached:</span>
                <p className={currentResponse.from_cache ? 'text-orange-600' : 'text-gray-600'}>
                  {currentResponse.from_cache ? 'Yes' : 'No'}
                </p>
              </div>
            </div>

            {currentResponse.suggestions && currentResponse.suggestions.length > 0 && (
              <div>
                <h4 className="font-medium mb-2 flex items-center">
                  <Lightbulb className="mr-2" size={16} />
                  Follow-up Suggestions:
                </h4>
                <ul className="list-disc list-inside space-y-1">
                  {currentResponse.suggestions.map((suggestion, index) => (
                    <li key={index} className="text-sm text-gray-600">{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Conversation History */}
      {conversationHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <History className="mr-2" size={18} />
            Conversation History ({conversationHistory.length} messages)
          </h3>
          
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {conversationHistory.slice(-6).map((message, index) => (
              <div
                key={index}
                className={`p-3 rounded-md ${
                  message.role === 'user' 
                    ? 'bg-blue-50 border-l-4 border-blue-500' 
                    : 'bg-green-50 border-l-4 border-green-500'
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-medium text-sm">
                    {message.role === 'user' ? 'You' : 'AI'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm">{message.content.substring(0, 200)}...</p>
                {message.metadata?.strategy && (
                  <span className="text-xs text-blue-600 mt-1 inline-block">
                    Strategy: {message.metadata.strategy}
                  </span>
                )}
              </div>
            ))}
          </div>
          
          <button
            onClick={analyzeContext}
            className="mt-4 px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 flex items-center"
            disabled={isLoading}
          >
            <BarChart3 className="mr-2" size={16} />
            Analyze Context
          </button>
        </div>
      )}
    </div>
  ), [query, currentResponse, conversationHistory, isLoading, generateResponse, analyzeContext]);

  const AnalyticsPanel = useMemo(() => (
    <div className="space-y-6">
      {/* Performance Metrics */}
      {performanceMetrics && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <TrendingUp className="mr-2" size={20} />
            Performance Metrics
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-md">
              <h3 className="font-medium text-blue-800">Total Requests</h3>
              <p className="text-2xl font-bold text-blue-600">{performanceMetrics.total_requests}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-md">
              <h3 className="font-medium text-green-800">Cache Hit Rate</h3>
              <p className="text-2xl font-bold text-green-600">{performanceMetrics.cache_hit_rate}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-md">
              <h3 className="font-medium text-purple-800">Avg Processing</h3>
              <p className="text-2xl font-bold text-purple-600">
                {performanceMetrics.average_processing_time_ms.toFixed(1)}ms
              </p>
            </div>
            <div className="bg-orange-50 p-4 rounded-md">
              <h3 className="font-medium text-orange-800">Context Quality</h3>
              <p className="text-2xl font-bold text-orange-600">{performanceMetrics.average_context_quality}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-md">
              <h3 className="font-medium text-red-800">Cache Size</h3>
              <p className="text-2xl font-bold text-red-600">{performanceMetrics.cache_size}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-md">
              <h3 className="font-medium text-gray-800">Status</h3>
              <p className="text-2xl font-bold text-gray-600">{performanceMetrics.service_status}</p>
            </div>
          </div>

          <button
            onClick={clearCache}
            className="mt-4 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 flex items-center"
          >
            <RefreshCw className="mr-2" size={16} />
            Clear Cache
          </button>
        </div>
      )}

      {/* Context Analysis */}
      {contextAnalysis && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Eye className="mr-2" size={20} />
            Context Analysis
          </h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Quality Score</h3>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${contextAnalysis.quality_score * 100}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {(contextAnalysis.quality_score * 100).toFixed(1)}% context quality
              </p>
            </div>

            {contextAnalysis.recommendations && contextAnalysis.recommendations.length > 0 && (
              <div>
                <h3 className="font-medium mb-2">Recommendations</h3>
                <ul className="list-disc list-inside space-y-1">
                  {contextAnalysis.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm text-gray-600">{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium mb-2">Conversation Analysis</h3>
                <div className="bg-gray-50 p-3 rounded-md">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(contextAnalysis.conversation_analysis, null, 2)}
                  </pre>
                </div>
              </div>
              <div>
                <h3 className="font-medium mb-2">User Analysis</h3>
                <div className="bg-gray-50 p-3 rounded-md">
                  <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(contextAnalysis.user_analysis, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Strategies and Context Types */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Target className="mr-2" size={18} />
            Response Strategies
          </h3>
          <div className="space-y-2">
            {strategies.map((strategy, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-3">
                <h4 className="font-medium">{strategy.name}</h4>
                <p className="text-sm text-gray-600">{strategy.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Filter className="mr-2" size={18} />
            Context Types
          </h3>
          <div className="space-y-2">
            {contextTypes.map((type, index) => (
              <div key={index} className="border-l-4 border-green-500 pl-3">
                <h4 className="font-medium">{type.name}</h4>
                <p className="text-sm text-gray-600">{type.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  ), [performanceMetrics, contextAnalysis, strategies, contextTypes, clearCache]);

  const SimulationPanel = useMemo(() => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Zap className="mr-2" size={20} />
          Conversation Simulation
        </h2>
        
        <p className="text-gray-600 mb-4">
          Test how context awareness evolves throughout a conversation with predefined queries.
        </p>
        
        <button
          onClick={simulateConversation}
          disabled={isLoading}
          className="px-6 py-3 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 flex items-center"
        >
          {isLoading ? <RefreshCw className="animate-spin mr-2" size={16} /> : <Share2 className="mr-2" size={16} />}
          Run Simulation
        </button>
      </div>

      {simulationResults.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Simulation Results</h3>
          
          <div className="space-y-4">
            {simulationResults.map((result, index) => (
              <div key={index} className="border rounded-md p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium">Query {result.query_index + 1}</h4>
                  <span className="text-sm text-gray-500">
                    {result.response_data.processing_time_ms.toFixed(1)}ms
                  </span>
                </div>
                
                <p className="text-sm text-gray-700 mb-2">{result.query}</p>
                
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="font-medium">Strategy:</span>
                    <p className="text-blue-600">{result.response_data.strategy}</p>
                  </div>
                  <div>
                    <span className="font-medium">Confidence:</span>
                    <p className="text-green-600">
                      {(result.response_data.confidence_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <span className="font-medium">History:</span>
                    <p className="text-purple-600">{result.conversation_length} msgs</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  ), [simulationResults, isLoading, simulateConversation]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
            <Brain className="mr-3 text-blue-500" size={32} />
            Context-Aware AI Responses
          </h1>
          <p className="text-gray-600">
            Advanced AI response generation using conversation history and user profiles
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6 flex items-center">
            <AlertCircle className="text-red-500 mr-2" size={20} />
            <span className="text-red-700">{error}</span>
            <button 
              onClick={() => setError(null)} 
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'chat', label: 'Chat Interface', icon: MessageSquare },
                { id: 'profile', label: 'User Profile', icon: User },
                { id: 'analytics', label: 'Analytics', icon: BarChart3 },
                { id: 'simulation', label: 'Simulation', icon: Zap }
              ].map(tab => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <Icon className="mr-2" size={16} />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {activeTab === 'chat' && ChatInterface}
            {activeTab === 'analytics' && AnalyticsPanel}
            {activeTab === 'simulation' && SimulationPanel}
          </div>
          
          <div className="lg:col-span-1">
            {activeTab === 'profile' ? (
              UserProfileEditor
            ) : (
              <div className="space-y-6">
                {/* Quick Stats */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <Clock className="mr-2" size={18} />
                    Quick Stats
                  </h3>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Messages:</span>
                      <span className="font-medium">{conversationHistory.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Profile:</span>
                      <span className="font-medium">{userProfile.expertise_level}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Style:</span>
                      <span className="font-medium">{userProfile.communication_style}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Interests:</span>
                      <span className="font-medium">{userProfile.interests.length}</span>
                    </div>
                  </div>
                </div>

                {/* Service Status */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <CheckCircle className="mr-2 text-green-500" size={18} />
                    Service Status
                  </h3>
                  
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      <span className="text-sm">Context Analysis</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      <span className="text-sm">Response Generation</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      <span className="text-sm">Personalization</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                      <span className="text-sm">Cache System</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContextAwareAI;
