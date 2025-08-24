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
          
          {/* Main heading - improved visual hierarchy */}
          <div className="text-center mb-8 lg:mb-12">
            <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-blue-700 leading-none sm:leading-tight mb-6 px-2 opacity-0 animate-fadeIn">
              Where Intelligence Meets Impact—
              <br className="hidden sm:block" />
              <span className="text-blue-600">AI Accessible to Everyone1.</span>
            </h1>

            <p className="text-gray-600 text-base sm:text-lg lg:text-xl leading-relaxed max-w-4xl mx-auto px-4 opacity-0 animate-fadeInDelay">
              Democratizing artificial intelligence through our platform that bridges human ambition and technological possibility. 
              Access cutting-edge AI-agents while empowering developers to innovate and earn. 
              <span className="text-blue-700 font-semibold">Now with enhanced reliability and seamless user registration.</span>
            </p>
          </div>

          {/* Action buttons - enhanced mobile-first design */}
          <div className="mb-12 lg:mb-16 space-y-4 sm:space-y-0 sm:flex sm:flex-wrap sm:justify-center sm:gap-4 lg:gap-6 px-2">
            <button 
              onClick={handleTryForFree}
              className="btn-mobile-lg w-full sm:w-auto sm:min-w-[220px] bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-xl hover:from-blue-700 hover:to-blue-800 active:from-blue-800 active:to-blue-900 transition-all duration-300 font-bold shadow-lg hover:shadow-xl hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-blue-300"
            >
              <span className="flex items-center justify-center">
                🚀 Get Started Free
                <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </button>
            <button 
              onClick={handleJoinAsDeveloper}
              className="btn-mobile-lg w-full sm:w-auto sm:min-w-[220px] bg-gradient-to-r from-purple-600 to-purple-700 text-white px-8 py-4 rounded-xl hover:from-purple-700 hover:to-purple-800 active:from-purple-800 active:to-purple-900 transition-all duration-300 font-bold shadow-lg hover:shadow-xl hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-purple-300"
            >
              <span className="flex items-center justify-center">
                👨‍💻 Join as Developer
                <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </span>
            </button>
            <button 
              onClick={handleSeeHowItWorks}
              className="btn-mobile-lg w-full sm:w-auto sm:min-w-[220px] border-2 border-blue-600 text-blue-600 bg-white px-8 py-4 rounded-xl hover:bg-blue-50 active:bg-blue-100 transition-all duration-300 font-bold shadow-lg hover:shadow-xl hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-blue-300"
            >
              <span className="flex items-center justify-center">
                📖 See How It Works
                <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </span>
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
          <div className="lg:hidden space-y-6">
            
            {/* AI Feature highlight card */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 mx-2 border border-gray-100">
              <div className="text-center">
                <div className="mb-4 flex justify-center">
                  <img
                    src="https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/LogoW.png"
                    alt="CapeControl AI"
                    className="h-16 w-16 sm:h-20 sm:w-20"
                  />
                </div>
                <h3 className="text-xl sm:text-2xl font-bold text-gray-800 mb-4">AI That Understands</h3>
                <p className="text-gray-600 text-lg leading-relaxed mb-6">
                  Experience the future of artificial intelligence—context-aware, adaptive, and designed to amplify human potential.
                </p>
                
                {/* Feature icons - improved spacing and touch targets */}
                <div className="grid grid-cols-3 gap-4 sm:gap-6">
                  <div className="text-center">
                    <div className="w-14 h-14 sm:w-16 sm:h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 shadow-md">
                      <svg className="w-8 h-8 sm:w-10 sm:h-10" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="text-sm sm:text-base font-semibold text-gray-700">Lightning Fast</div>
                  </div>
                  <div className="text-center">
                    <div className="w-14 h-14 sm:w-16 sm:h-16 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mx-auto mb-3 shadow-md">
                      <svg className="w-8 h-8 sm:w-10 sm:h-10" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="text-sm sm:text-base font-semibold text-gray-700">Ultra Precise</div>
                  </div>
                  <div className="text-center">
                    <div className="w-14 h-14 sm:w-16 sm:h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-3 shadow-md">
                      <svg className="w-8 h-8 sm:w-10 sm:h-10" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="text-sm sm:text-base font-semibold text-gray-700">Global Scale</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Platform Stats - enhanced mobile section */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-2xl p-6 mx-2 text-white">
              <div className="text-center mb-6">
                <h3 className="text-lg sm:text-xl font-bold mb-2">Trusted by Thousands Worldwide</h3>
                <p className="text-blue-100 text-sm">Join the AI revolution today - Registration is live!</p>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-xl sm:text-2xl font-bold">2500+</div>
                  <div className="text-xs text-blue-100">Active Users</div>
                </div>
                <div className="text-center">
                  <div className="text-xl sm:text-2xl font-bold">75+</div>
                  <div className="text-xs text-blue-100">AI Agents</div>
                </div>
                <div className="text-center">
                  <div className="text-xl sm:text-2xl font-bold">99.9%</div>
                  <div className="text-xs text-blue-100">Uptime</div>
                </div>
              </div>
            </div>

            {/* Vision quote - enhanced mobile layout */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 sm:p-8 mx-2 border border-gray-100">
              <div className="text-center">
                <span className="text-blue-500 text-3xl sm:text-4xl leading-none">"</span>
                <p className="text-gray-700 italic text-base sm:text-lg leading-relaxed my-4">
                  CapeControl is more than a service—it's a showcase of what AI can achieve. 
                  The platform's intelligence and responsiveness demonstrate the transformative potential of AI.
                </p>
                <div className="text-right">
                  <div className="text-sm font-semibold text-gray-800">— Vision Statement</div>
                  <div className="text-xs text-gray-500">CapeControl Team</div>
                </div>
              </div>
            </div>

            {/* Final CTA - mobile optimized */}
            <div className="text-center mx-2">
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border-2 border-blue-200 shadow-xl">
                <p className="text-base sm:text-lg font-bold text-blue-700 mb-4 leading-relaxed">
                  "Where intelligence meets impact, and possibilities become realities."
                </p>
                <button 
                  onClick={handleTryForFree}
                  className="w-full sm:w-auto bg-blue-600 text-white px-8 py-4 min-h-[54px] rounded-xl hover:bg-blue-700 transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-blue-300"
                >
                  Start Your AI Journey
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}
