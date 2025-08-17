import React from 'react';

class ContextErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Check if this is a React context or DOM manipulation error
    if (error?.message?.includes('useContext') || 
        error?.message?.includes('Provider') ||
        error?.message?.includes('Context') ||
        error?.message?.includes('removeChild') ||
        error?.message?.includes('Minified React error')) {
      return { hasError: true, error };
    }
    // For other errors, let them bubble up
    return null;
  }

  componentDidCatch(error, errorInfo) {
    console.warn('🛡️ Error Boundary caught error:', error, errorInfo);
    console.warn('🛡️ Error details:', {
      message: error?.message,
      stack: error?.stack,
      name: error?.name
    });
    this.setState({ errorInfo });
    
    // Try to recover after a short delay
    setTimeout(() => {
      this.setState({ hasError: false, error: null, errorInfo: null });
    }, 3000);
  }

  render() {
    if (this.state.hasError) {
      // Safe fallback when errors occur
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md mx-auto p-6 text-center bg-white rounded-lg shadow-lg">
            <div className="text-4xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-gray-800 mb-3">Something went wrong</h2>
            <p className="text-gray-600 text-sm mb-4">
              The application encountered an error. It will automatically recover in a moment.
            </p>
            {this.state.error && (
              <details className="text-xs text-gray-500 mb-4 text-left">
                <summary className="cursor-pointer">Error details (for debugging)</summary>
                <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                  {this.state.error.message}
                </pre>
              </details>
            )}
            <button 
              onClick={() => window.location.reload()} 
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ContextErrorBoundary;
