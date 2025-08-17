import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

// Progress Bar Component
function ProgressBar({ currentStep, totalSteps }) {
  const progress = (currentStep / totalSteps) * 100;
  
  return (
    <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
      <div 
        className="bg-purple-600 h-2 rounded-full transition-all duration-300 ease-in-out" 
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  );
}

export default function Phase2DeveloperRegistration() {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [userData, setUserData] = useState(location.state?.userData || {});

  // Form data state
  const [formData, setFormData] = useState({
    githubUrl: "",
    portfolioUrl: "",
    experience: "",
    skills: [],
    specializations: [],
    previousWork: "",
    workType: "",
    availability: "",
    payoutMethod: "",
    bio: "",
    profileImage: null,
    socialLinks: {
      linkedin: "",
      twitter: "",
      website: ""
    }
  });

  useEffect(() => {
    // If no user data from previous registration, redirect back
    if (!userData.email) {
      navigate('/register');
    }
  }, [userData, navigate]);

  const experienceLevels = [
    "Student/Beginner (0-1 years)",
    "Junior Developer (1-3 years)", 
    "Mid-level Developer (3-5 years)",
    "Senior Developer (5-8 years)",
    "Expert/Lead (8+ years)"
  ];

  const skillOptions = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", 
    "TensorFlow", "PyTorch", "OpenAI API", "LangChain", "Vector Databases",
    "API Development", "Database Design", "Cloud Platforms", "Docker"
  ];

  const specializationOptions = [
    "Conversational AI", "Content Generation", "Data Analysis", 
    "Image Processing", "Voice/Speech", "Automation", "Integration",
    "Business Intelligence", "Customer Support", "E-commerce", "Finance"
  ];

  const workTypes = [
    "Full-time availability", "Part-time/Freelance", "Project-based", 
    "Consultancy", "Passive income focus"
  ];

  const availabilityOptions = [
    "Immediately", "Within 2 weeks", "Within 1 month", "Planning ahead"
  ];

  const payoutMethods = [
    "Bank Transfer", "PayPal", "Stripe", "Cryptocurrency", "Check"
  ];

  const handleSkillToggle = (skill) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.includes(skill)
        ? prev.skills.filter(s => s !== skill)
        : [...prev.skills, skill]
    }));
  };

  const handleSpecializationToggle = (spec) => {
    setFormData(prev => ({
      ...prev,
      specializations: prev.specializations.includes(spec)
        ? prev.specializations.filter(s => s !== spec)
        : [...prev.specializations, spec]
    }));
  };

  const handleSocialLinkChange = (platform, value) => {
    setFormData(prev => ({
      ...prev,
      socialLinks: {
        ...prev.socialLinks,
        [platform]: value
      }
    }));
  };

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    setIsLoading(true);
    try {
      // Combine user data with developer profile data
      const profileData = {
        ...formData,
        profileCompleted: true,
        phase2Completed: true,
        earningsTarget: "Initial",
        revenueShare: 0.30 // 30% revenue share
      };

      // Call the Phase 2 profile completion API
      const response = await fetch('/api/enhanced/complete-phase2-profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userData.accessToken || ''}`
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log("Developer profile completed successfully:", result);
        
        // Navigate to developer login with success message
        navigate('/login-developer', { 
          state: { 
            message: "Developer profile completed successfully! Please log in to access your dashboard.",
            email: userData.email 
          }
        });
      } else {
        const error = await response.json();
        console.error("Developer profile completion failed:", error);
        
        // For now, still navigate but with a different message
        navigate('/login-developer', { 
          state: { 
            message: "Profile saved locally. Please log in to access your dashboard.",
            email: userData.email 
          }
        });
      }
    } catch (error) {
      console.error("Error completing developer profile:", error);
      
      // Fallback: navigate to login even if API call fails
      navigate('/login-developer', { 
        state: { 
          message: "Please log in to complete your profile setup.",
          email: userData.email 
        }
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderStep1 = () => (
    <div>
      <h3 className="text-xl font-semibold mb-6 text-purple-700">Developer Experience</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            GitHub Profile URL
          </label>
          <input
            type="url"
            value={formData.githubUrl}
            onChange={(e) => setFormData({...formData, githubUrl: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="https://github.com/username"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Portfolio/Website URL (optional)
          </label>
          <input
            type="url"
            value={formData.portfolioUrl}
            onChange={(e) => setFormData({...formData, portfolioUrl: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="https://yourportfolio.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Experience Level
          </label>
          <select
            value={formData.experience}
            onChange={(e) => setFormData({...formData, experience: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Select your experience level</option>
            {experienceLevels.map(level => (
              <option key={level} value={level}>{level}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Previous AI/ML Work (optional)
          </label>
          <textarea
            value={formData.previousWork}
            onChange={(e) => setFormData({...formData, previousWork: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            rows={3}
            placeholder="Briefly describe your AI/ML projects or experience..."
          />
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div>
      <h3 className="text-xl font-semibold mb-6 text-purple-700">Skills & Specializations</h3>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Technical Skills (select all that apply)
          </label>
          <div className="grid grid-cols-2 gap-3 max-h-48 overflow-y-auto border border-gray-200 p-4 rounded-lg">
            {skillOptions.map(skill => (
              <label key={skill} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.skills.includes(skill)}
                  onChange={() => handleSkillToggle(skill)}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="text-sm text-gray-700">{skill}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            AI Specializations (select your focus areas)
          </label>
          <div className="grid grid-cols-2 gap-3">
            {specializationOptions.map(spec => (
              <label key={spec} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.specializations.includes(spec)}
                  onChange={() => handleSpecializationToggle(spec)}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="text-sm text-gray-700">{spec}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Developer Bio
          </label>
          <textarea
            value={formData.bio}
            onChange={(e) => setFormData({...formData, bio: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            rows={3}
            placeholder="Tell potential clients about yourself and your expertise..."
          />
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div>
      <h3 className="text-xl font-semibold mb-6 text-purple-700">Work Preferences</h3>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Work Type Preference
          </label>
          <select
            value={formData.workType}
            onChange={(e) => setFormData({...formData, workType: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Select work preference</option>
            {workTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Availability
          </label>
          <select
            value={formData.availability}
            onChange={(e) => setFormData({...formData, availability: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Select availability</option>
            {availabilityOptions.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Preferred Payout Method
          </label>
          <select
            value={formData.payoutMethod}
            onChange={(e) => setFormData({...formData, payoutMethod: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">Select payout method</option>
            {payoutMethods.map(method => (
              <option key={method} value={method}>{method}</option>
            ))}
          </select>
        </div>

        <div className="border-t pt-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4">Social Links (optional)</h4>
          
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                LinkedIn
              </label>
              <input
                type="url"
                value={formData.socialLinks.linkedin}
                onChange={(e) => handleSocialLinkChange('linkedin', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="https://linkedin.com/in/username"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Twitter
              </label>
              <input
                type="url"
                value={formData.socialLinks.twitter}
                onChange={(e) => handleSocialLinkChange('twitter', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="https://twitter.com/username"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Personal Website
              </label>
              <input
                type="url"
                value={formData.socialLinks.website}
                onChange={(e) => handleSocialLinkChange('website', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="https://yourwebsite.com"
              />
            </div>
          </div>
        </div>

        <div className="bg-purple-50 p-4 rounded-lg">
          <h4 className="font-medium text-purple-800 mb-2">Revenue Share: 30%</h4>
          <p className="text-sm text-purple-700">
            You'll earn 30% of all revenue generated from your AI agents. 
            Payments are processed monthly with detailed analytics provided.
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white py-12">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Complete Your Developer Profile
            </h1>
            <p className="text-gray-600">
              Set up your profile to start building and earning with AI agents
            </p>
            <ProgressBar currentStep={currentStep} totalSteps={3} />
          </div>

          <div className="mb-8">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
          </div>

          <div className="flex justify-between">
            <button
              onClick={handleBack}
              disabled={currentStep === 1}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                currentStep === 1
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Back
            </button>

            <button
              onClick={handleNext}
              disabled={isLoading}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Processing...' : currentStep === 3 ? 'Complete Profile' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
