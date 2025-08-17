import { useNavigate } from 'react-router-dom';

export default function HeroSafe() {
  const navigate = useNavigate();

  const handleSeeHowItWorks = () => {
    navigate('/how-it-works');
  };

  const handleTryForFree = () => {
    navigate('/register');
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

          {/* Action buttons - mobile-optimized */}
          <div className="mb-12 lg:mb-16 flex flex-col sm:flex-row justify-center gap-4 px-2">
            <button 
              onClick={handleTryForFree}
              className="w-full sm:w-auto bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors text-lg font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-transform"
            >
              Get Started Free
            </button>
            <button 
              onClick={() => navigate('/developers')}
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
                    <div className="text-sm font-semibold text-gray-700">Global Scale</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Platform Stats - new mobile section */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-6 mx-2 text-white">
              <div className="text-center mb-6">
                <h3 className="text-xl font-bold mb-2">Trusted by Thousands</h3>
                <p className="text-blue-100 text-sm">Join the AI revolution today</p>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">1000+</div>
                  <div className="text-xs text-blue-100">Active Users</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">50+</div>
                  <div className="text-xs text-blue-100">AI Agents</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">24/7</div>
                  <div className="text-xs text-blue-100">Support</div>
                </div>
              </div>
            </div>

            {/* Vision quote - enhanced */}
            <div className="bg-white rounded-2xl shadow-xl p-8 mx-2">
              <div className="text-center">
                <span className="text-blue-500 text-4xl leading-none">"</span>
                <p className="text-gray-700 italic text-lg leading-relaxed my-4">
                  CapeControl is more than a service—it's a showcase of what AI can achieve. 
                  The platform's intelligence and responsiveness demonstrate the transformative potential of AI.
                </p>
                <div className="text-right">
                  <div className="text-sm font-semibold text-gray-800">— Vision Statement</div>
                  <div className="text-xs text-gray-500">CapeControl Team</div>
                </div>
              </div>
            </div>

            {/* Final CTA - mobile */}
            <div className="text-center mx-2">
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-200">
                <p className="text-lg font-bold text-blue-700 mb-4">
                  "Where intelligence meets impact, and possibilities become realities."
                </p>
                <button 
                  onClick={handleTryForFree}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-lg"
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
