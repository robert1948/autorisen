import React from 'react';
import { Link } from 'react-router-dom';
import TopNav from './nav/TopNav';
import Footer from './Footer';

const HomePage: React.FC = () => {
  const handleOpenSupport = () => {
    console.log("Open support chat");
    // In a full implementation, this would toggle the chat modal
  };

  return (
    <div className="min-h-screen flex flex-col font-sans text-gray-800">
      <TopNav onOpenSupport={handleOpenSupport} />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-[#667eea] to-[#764ba2] text-white text-center py-24 px-5">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
            Reframe Your AI Journey: From Overwhelm to Effortless Magic
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90">
            In a world of complex integrations and compliance nightmares, CapeControl turns AI into your intuitive ally. No more "range anxiety"—just seamless onboarding, secure querying, and compliant agents that feel like a genius whisper in your ear.
          </p>
          <div className="inline-block bg-white/10 p-2 rounded-xl backdrop-blur-sm">
            <Link 
              to="/register" 
              className="block bg-[#ff6b6b] hover:bg-[#ff5252] text-white px-8 py-4 rounded-lg font-bold text-lg transition-colors shadow-lg"
            >
              Start Your Free Magic Trial
            </Link>
          </div>
        </div>
      </section>

      {/* The Alchemy of AI */}
      <section className="py-20 px-5 max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">Rationality Gets You Bronze. Magic Gets You Gold.</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Inspired by Rory Sutherland's <em>Alchemy</em>, we know engineering alone won't transform your business. It's the psychological spark—the reframing, the surprise—that drives adoption. CapeControl isn't just faster AI; it's AI that <em>feels</em> liberating.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-10">
          <div className="text-center">
            <img src="https://via.placeholder.com/200x200?text=Anxiety+Antidote" alt="AI Anxiety Reframed" className="mx-auto rounded-xl mb-6 shadow-md" />
            <h3 className="text-2xl font-bold text-[#667eea] mb-3">Tame AI Anxiety</h3>
            <p className="text-gray-600">Like neon-lit charging stations for EVs, our guided onboarding lights up compliance paths—reducing setup dread by 70%.</p>
          </div>
          <div className="text-center">
            <img src="https://via.placeholder.com/200x200?text=Surprise+Insights" alt="Magical Queries" className="mx-auto rounded-xl mb-6 shadow-md" />
            <h3 className="text-2xl font-bold text-[#764ba2] mb-3">Query with Magic</h3>
            <p className="text-gray-600">Intuitive data chats for energy and finance pros. Turn complex spreadsheets into "aha!" moments—no PhD required.</p>
          </div>
          <div className="text-center">
            <img src="https://via.placeholder.com/200x200?text=Secure+Agents" alt="Compliant Agents" className="mx-auto rounded-xl mb-6 shadow-md" />
            <h3 className="text-2xl font-bold text-[#ff6b6b] mb-3">Agents That Delight</h3>
            <p className="text-gray-600">Modular, secure AI agents for devs. Build compliant bots that surprise with efficiency, not errors.</p>
          </div>
        </div>
      </section>

      {/* Reverse Benchmark */}
      <section className="bg-gray-50 py-20 px-5">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">We Don't Copy the Best. We Fix the Worst.</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-16">
            Competitors nail power but flop on joy. We reverse-engineer the letdowns—like Buc-ee's brilliant restrooms in a sea of mediocrity.
          </p>

          <div className="grid md:grid-cols-3 gap-8 text-left">
            <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <h3 className="text-2xl font-bold text-[#667eea] mb-4">Clunky Onboarding? Nah.</h3>
              <p className="text-gray-600">Our "Guided Onboarding Theater" feels like a witty concierge—personalized, playful, and 4x faster adoption.</p>
            </div>
            <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <h3 className="text-2xl font-bold text-[#764ba2] mb-4">Boring Compliance? Think Again.</h3>
              <p className="text-gray-600">"Compliance as Comedy": Videos and tools that make red tape feel like a spy thriller. Secure, but surprisingly fun.</p>
            </div>
            <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <h3 className="text-2xl font-bold text-[#ff6b6b] mb-4">Rigid Tools? Playtime Awaits.</h3>
              <p className="text-gray-600">"Agent Playground": Free sandbox for wild, compliant creations. Devs build memes from finance data—innovation unlocked.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Explore the Magic */}
      <section className="py-20 px-5 max-w-5xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">Balance the Hive: Exploit Efficiency, Explore Surprises</h2>
        <p className="text-xl text-gray-600 mb-12">
          Like bees scouting new fields, we blend proven ROI with lucky bets. Your AI won't starve in local maxima—it'll thrive on fat-tailed wins.
        </p>

        <div className="flex flex-col md:flex-row justify-center items-center gap-8 mb-12">
          <div className="w-64 h-64 rounded-full bg-[#667eea] flex flex-col items-center justify-center text-white text-2xl font-bold shadow-xl">
            <span>80%</span>
            <span>Exploit</span>
            <span>Efficiency</span>
          </div>
          <div className="w-64 h-64 rounded-full bg-[#ff6b6b] flex flex-col items-center justify-center text-white text-2xl font-bold shadow-xl">
            <span>20%</span>
            <span>Explore</span>
            <span>Magic</span>
          </div>
        </div>

        <p className="text-lg text-gray-700">
          Join our AI Alchemist Circles: Share "magic moments" with peers in finance and energy. One surprise insight could 4x your processes.
        </p>
      </section>

      {/* The Human Spark */}
      <section className="bg-gradient-to-br from-[#ff9a9e] to-[#fecfef] py-20 px-5 text-center">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">AI Automates. Humans Enchant.</h2>
          <p className="text-xl text-gray-800 mb-8">
            As algorithms rule, one genuine "posty" moment—a trusted chat with our AI Whisperer—creates brand quakes that last.
          </p>
          <div className="inline-block bg-white p-2 rounded-xl shadow-md">
            <button onClick={handleOpenSupport} className="block text-[#667eea] px-8 py-3 font-bold text-lg hover:bg-gray-50 rounded-lg transition-colors">
              Book a Surprise Discovery Chat
            </button>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-5 text-center bg-white">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">Ignite Your Alchemy</h2>
        <p className="text-xl text-gray-600 mb-10">Perceptions shift. Behaviors follow. Worlds transform.</p>
        
        <Link 
          to="/register" 
          className="inline-block bg-[#667eea] hover:bg-[#5a6fd6] text-white px-10 py-4 rounded-lg font-bold text-lg shadow-lg transition-all transform hover:-translate-y-1"
        >
          Get Started Free – No Card Needed
        </Link>
        
        <p className="mt-10 text-sm text-gray-400">
          Trusted by 500+ enterprises in finance & energy | © 2025 CapeControl
        </p>
      </section>

      {/* Quote Section */}
      <div className="bg-[#333] text-white text-center py-6 px-4">
        <p className="text-lg italic opacity-80">"Ideas that don't make sense... until they do." – Inspired by Rory Sutherland</p>
      </div>

      <Footer onOpenSupport={handleOpenSupport} />
    </div>
  );
};

export default HomePage;
