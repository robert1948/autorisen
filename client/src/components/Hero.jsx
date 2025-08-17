import { useNavigate } from 'react-router-dom';

export default function Hero() {
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
      <div className="flex-1 flex flex-col justify-center px-4 pt-24 pb-8 lg:pt-32 lg:pb-16">
        <div className="max-w-4xl mx-auto w-full">
          
          {/* Main heading - optimized for mobile */}
          <div className="text-center mb-6 lg:mb-8">
            <h1 className="text-2xl sm:text-3xl lg:text-5xl font-extrabold text-blue-700 leading-tight mb-4">
              Where Intelligence Meets Impact—
              <br />
              <span className="text-blue-600">AI Accessible to Everyone.</span>
            </h1>

            <p className="text-gray-600 text-sm sm:text-base lg:text-xl leading-relaxed max-w-2xl mx-auto">
              Democratizing artificial intelligence through our platform that bridges human ambition and technological possibility. 
              Access cutting-edge AI-agents while empowering developers to innovate and earn.
            </p>
          </div>

          {/* Action buttons - full width on mobile */}
          <div className="mb-8 lg:mb-12 space-y-3 sm:space-y-0 sm:flex sm:justify-center sm:gap-3 lg:gap-4">
            <button 
              onClick={handleTryForFree}
              className="w-full sm:w-auto bg-blue-600 text-white px-6 py-3 lg:px-8 lg:py-4 rounded-lg hover:bg-blue-700 transition-colors text-base lg:text-lg font-semibold"
            >
              Get Started Free
            </button>
            <button 
              onClick={() => navigate('/developers')}
              className="w-full sm:w-auto bg-purple-600 text-white px-6 py-3 lg:px-8 lg:py-4 rounded-lg hover:bg-purple-700 transition-colors text-base lg:text-lg font-semibold"
            >
              Join as Developer
            </button>
            <button 
              onClick={handleSeeHowItWorks}
              className="w-full sm:w-auto border border-blue-600 text-blue-600 px-6 py-3 lg:px-8 lg:py-4 rounded-lg hover:bg-blue-50 transition-colors text-base lg:text-lg font-semibold"
            >
              See How It Works
            </button>
          </div>

          {/* Desktop image - hidden on mobile */}
          <div className="hidden lg:block bg-white rounded-xl shadow-lg mx-auto w-full max-w-4xl overflow-hidden mb-8">
            <img
              src="https://lightning-s3.s3.us-east-1.amazonaws.com/static/website/img/landing01.png"
              alt="CapeControl Platform - AI That Understands"
              className="w-full h-auto"
              loading="lazy"
              decoding="async"
              width="1000"
              height="600"
            />
            <div className="py-4 text-sm text-gray-700 font-medium bg-gray-50 text-center">
              Platform Preview • Where Intelligence Meets Impact
            </div>
          </div>

          {/* Mobile-optimized content stack */}
          <div className="lg:hidden space-y-6">
            
            {/* AI Feature highlight card */}
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-4xl mb-3 text-blue-600">🤖</div>
              <h3 className="text-xl font-bold text-gray-800 mb-3">AI That Understands</h3>
              <p className="text-gray-600 text-sm leading-relaxed mb-6">
                Experience the future of artificial intelligence—context-aware, adaptive, and designed to amplify human potential.
              </p>
              
              {/* Feature icons */}
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-2">⚡</div>
                  <div className="text-xs font-medium text-gray-700">Fast</div>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mx-auto mb-2">🎯</div>
                  <div className="text-xs font-medium text-gray-700">Precise</div>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-2">🌐</div>
                  <div className="text-xs font-medium text-gray-700">Global</div>
                </div>
              </div>
            </div>

            {/* Trust indicator */}
            <div className="text-center">
              <div className="flex justify-center items-center gap-2 text-gray-500 text-sm">
                <span className="text-yellow-500">⭐</span>
                <span>Empowering developers and businesses worldwide</span>
              </div>
            </div>

            {/* Vision quote */}
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <span className="text-blue-500 text-2xl">"</span>
              <p className="text-gray-700 italic text-sm leading-relaxed mb-3">
                CapeControl is more than a service—it's a showcase of what AI can achieve. 
                The platform's intelligence and responsiveness demonstrate the transformative potential of AI.
              </p>
              <div className="text-right text-xs font-medium text-gray-600">
                — From our Vision Statement
              </div>
            </div>

            {/* Vision tagline */}
            <div className="text-center">
              <p className="text-base font-medium text-blue-700">
                "Where intelligence meets impact, and possibilities become realities."
              </p>
            </div>

          </div>
        </div>
      </div>
    </section>
  );
}