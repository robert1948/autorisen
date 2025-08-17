import React from 'react';
import { useNavigate } from 'react-router-dom';

// Safe navigation hook that handles context errors
function useSafeNavigate() {
  try {
    const navigate = useNavigate();
    return navigate;
  } catch (error) {
    console.warn('Navigation context not available, using fallback:', error);
    // Fallback to window.location for navigation
    return (path) => {
      try {
        window.location.href = path;
      } catch (e) {
        console.error('Navigation failed:', e);
      }
    };
  }
}

export default function Landing() {
  const navigate = useSafeNavigate();

  const handleSeeHowItWorks = () => {
    try {
      navigate('/how-it-works');
    } catch (error) {
      console.error('Navigation error:', error);
      window.location.href = '/how-it-works';
    }
  };

  const handleTryForFree = () => {
    try {
      navigate('/register');
    } catch (error) {
      console.error('Navigation error:', error);
      window.location.href = '/register';
    }
  };

  const handleJoinAsDeveloper = () => {
    try {
      navigate('/developers');
    } catch (error) {
      console.error('Navigation error:', error);
      window.location.href = '/developers';
    }
  };

  return (
    <section className="min-h-screen bg-gradient-to-b from-white to-blue-50 flex flex-col">
      {/* Mobile-first layout with proper spacing */}
      <div className="flex-1 flex flex-col justify-center px-4 pt-20 pb-8 sm:pt-24 lg:pt-32 lg:pb-16">
        <div className="max-w-5xl mx-auto w-full">
          
          {/* Main heading - optimized for mobile */}
          <div className="text-center mb-8 lg:mb-12">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold text-blue-700 leading-tight mb-6">
              Where Intelligence Meets Impact—
              <br className="hidden sm:block" />
              <span className="text-blue-600">AI Accessible to Everyone.</span>
            </h1>

            <p className="text-gray-600 text-base sm:text-lg lg:text-xl leading-relaxed max-w-3xl mx-auto px-2">
              Democratizing artificial intelligence through our platform that bridges human ambition and technological possibility. 
              Access cutting-edge AI-agents while empowering developers to innovate and earn.
            </p>
          </div>

          {/* Action buttons - full width on mobile, enhanced for touch */}
          <div className="mb-12 lg:mb-16 space-y-4 sm:space-y-0 sm:flex sm:flex-wrap sm:justify-center sm:gap-4 lg:gap-6">
            <button 
              onClick={handleTryForFree}
              className="w-full sm:w-auto bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform"
            >
              Get Started Free
            </button>
            <button 
              onClick={handleJoinAsDeveloper}
              className="w-full sm:w-auto bg-purple-600 text-white px-8 py-4 rounded-lg hover:bg-purple-700 active:bg-purple-800 transition-colors text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform"
            >
              Join as Developer
            </button>
            <button 
              onClick={handleSeeHowItWorks}
              className="w-full sm:w-auto border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-lg hover:bg-blue-50 active:bg-blue-100 transition-colors text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform"
            >
              See How It Works
            </button>
          </div>

          {/* Desktop image - enhanced with better responsive handling */}
          <div className="hidden lg:block bg-white rounded-2xl shadow-2xl mx-auto w-full max-w-5xl overflow-hidden mb-12">
            <img
              src="https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/landing01.png"
              alt="CapeControl Platform - AI That Understands"
              className="w-full h-auto"
              loading="lazy"
              decoding="async"
              width="1200"
              height="700"
            />
            <div className="py-6 text-center bg-gradient-to-r from-blue-50 to-purple-50">
              <p className="text-gray-700 font-semibold text-lg">Platform Preview</p>
              <p className="text-blue-600 font-medium">Where Intelligence Meets Impact</p>
            </div>
          </div>

          {/* Mobile-optimized content stack - enhanced */}
          <div className="lg:hidden space-y-8">
            
            {/* AI Feature highlight card */}
            <div className="bg-white rounded-2xl shadow-xl p-6 mx-2">
              <div className="text-center">
                <div className="text-5xl mb-4 text-blue-600">🤖</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-4">AI That Understands</h3>
                <p className="text-gray-600 text-base leading-relaxed mb-8">
                  Experience the future of artificial intelligence—context-aware, adaptive, and designed to amplify human potential.
                </p>
                
                {/* Feature icons - improved spacing */}
                <div className="grid grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl">⚡</div>
                    <div className="text-sm font-semibold text-gray-700">Lightning Fast</div>
                  </div>
                  <div className="text-center">
                    <div className="w-16 h-16 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl">🎯</div>
                    <div className="text-sm font-semibold text-gray-700">Ultra Precise</div>
                  </div>
                  <div className="text-center">
                    <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl">🌐</div>
                    <div className="text-sm font-semibold text-gray-700">Always Available</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Developer platform highlight */}
            <div className="bg-white rounded-2xl shadow-xl p-6 mx-2">
              <div className="text-center">
                <div className="text-5xl mb-4 text-purple-600">👨‍💻</div>
                <h3 className="text-2xl font-bold text-gray-800 mb-4">Developer Empowerment</h3>
                <p className="text-gray-600 text-base leading-relaxed mb-6">
                  Build, deploy, and monetize AI agents on our platform. Join a community where your innovations create impact and income.
                </p>
                
                <div className="space-y-4">
                  <div className="flex items-center bg-purple-50 rounded-lg p-4">
                    <div className="text-2xl mr-4">💰</div>
                    <div className="text-left">
                      <div className="font-semibold text-gray-800">Earn While You Build</div>
                      <div className="text-sm text-gray-600">Monetize your AI creations</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center bg-blue-50 rounded-lg p-4">
                    <div className="text-2xl mr-4">🚀</div>
                    <div className="text-left">
                      <div className="font-semibold text-gray-800">Deploy with Ease</div>
                      <div className="text-sm text-gray-600">One-click deployment platform</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* CTA for mobile */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 mx-2 text-white text-center">
              <h3 className="text-2xl font-bold mb-4">Ready to Transform Your Ideas?</h3>
              <p className="text-blue-100 mb-6 leading-relaxed">
                Join thousands who are already building the future with AI that truly understands.
              </p>
              <div className="space-y-3">
                <button 
                  onClick={handleTryForFree}
                  className="w-full bg-white text-blue-600 px-6 py-3 rounded-lg hover:bg-blue-50 active:bg-blue-100 transition-colors font-semibold shadow-lg"
                >
                  Start Your Journey Free
                </button>
                <button 
                  onClick={handleJoinAsDeveloper}
                  className="w-full border-2 border-white text-white px-6 py-3 rounded-lg hover:bg-white hover:text-purple-600 active:bg-blue-50 transition-colors font-semibold"
                >
                  Become a Developer
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* Footer with enhanced mobile design */}
      <footer className="bg-gray-900 text-white py-8 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <div className="text-2xl font-bold mb-4 text-blue-400">CapeControl</div>
          <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
            Democratizing AI technology to empower individuals and businesses worldwide.
          </p>
          
          {/* Social proof numbers - mobile optimized */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">10K+</div>
              <div className="text-gray-400 text-sm">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">500+</div>
              <div className="text-gray-400 text-sm">AI Agents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">99.9%</div>
              <div className="text-gray-400 text-sm">Uptime</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">24/7</div>
              <div className="text-gray-400 text-sm">Support</div>
            </div>
          </div>
          
          <div className="text-gray-500 text-sm">
            © 2024 CapeControl. Transforming possibilities into reality.
          </div>
        </div>
      </footer>
    </section>
  );
}
