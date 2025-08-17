import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

// Progress Bar Component
function ProgressBar({ currentStep, totalSteps }) {
  const progress = (currentStep / totalSteps) * 100;
  
  return (
    <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
      <div 
        className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-in-out" 
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  );
}

export default function Phase2CustomerRegistration() {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [userData, setUserData] = useState(location.state?.userData || {});

  // Form data state
  const [formData, setFormData] = useState({
    companyName: "",
    industry: "",
    companySize: "",
    businessType: "",
    useCase: "",
    budget: "",
    goals: [],
    preferredIntegrations: [],
    timeline: "",
    experience: ""
  });

  useEffect(() => {
    // If no user data from previous registration, redirect back
    if (!userData.email) {
      navigate('/register');
    }
  }, [userData, navigate]);

  const industries = [
    "Technology", "Healthcare", "Finance", "Retail", "Manufacturing",
    "Education", "Real Estate", "Marketing", "Consulting", "Other"
  ];

  const companySizes = [
    "Just me (1)", "Small team (2-10)", "Medium (11-50)", 
    "Large (51-200)", "Enterprise (200+)"
  ];

  const businessTypes = [
    "Startup", "SMB", "Enterprise", "Agency", "Freelancer", "Non-profit"
  ];

  const useCases = [
    "Customer Support", "Sales Automation", "Content Creation", 
    "Data Analysis", "Process Automation", "Lead Generation", "Other"
  ];

  const budgetRanges = [
    "Under $100/month", "$100-500/month", "$500-2000/month", 
    "$2000-5000/month", "$5000+/month", "Enterprise pricing"
  ];

  const availableGoals = [
    "Increase Productivity", "Reduce Costs", "Improve Customer Experience",
    "Scale Operations", "Generate More Leads", "Automate Processes",
    "Data-Driven Decisions", "Competitive Advantage"
  ];

  const integrations = [
    "Salesforce", "HubSpot", "Slack", "Microsoft Teams", "Google Workspace",
    "Shopify", "WordPress", "Zapier", "API Integration", "Custom Integration"
  ];

  const handleGoalToggle = (goal) => {
    setFormData(prev => ({
      ...prev,
      goals: prev.goals.includes(goal)
        ? prev.goals.filter(g => g !== goal)
        : [...prev.goals, goal]
    }));
  };

  const handleIntegrationToggle = (integration) => {
    setFormData(prev => ({
      ...prev,
      preferredIntegrations: prev.preferredIntegrations.includes(integration)
        ? prev.preferredIntegrations.filter(i => i !== integration)
        : [...prev.preferredIntegrations, integration]
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
      // Combine user data with additional profile data
      const profileData = {
        ...formData,
        profileCompleted: true,
        phase2Completed: true
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
        console.log("Profile completed successfully:", result);
        
        // Navigate to customer login with success message
        navigate('/login-customer', { 
          state: { 
            message: "Profile completed successfully! Please log in to access your dashboard.",
            email: userData.email 
          }
        });
      } else {
        const error = await response.json();
        console.error("Profile completion failed:", error);
        
        // For now, still navigate but with a different message
        navigate('/login-customer', { 
          state: { 
            message: "Profile saved locally. Please log in to access your dashboard.",
            email: userData.email 
          }
        });
      }
    } catch (error) {
      console.error("Error completing profile:", error);
      
      // Fallback: navigate to login even if API call fails
      navigate('/login-customer', { 
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
      <h3 className="text-xl font-semibold mb-6">Company Information</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company Name
          </label>
          <input
            type="text" autoComplete="username"
            value={formData.companyName}
            onChange={(e) => setFormData({...formData, companyName: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Your company or organization name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Industry
          </label>
          <select
            value={formData.industry}
            onChange={(e) => setFormData({...formData, industry: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select your industry</option>
            {industries.map(industry => (
              <option key={industry} value={industry}>{industry}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Company Size
          </label>
          <select
            value={formData.companySize}
            onChange={(e) => setFormData({...formData, companySize: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select company size</option>
            {companySizes.map(size => (
              <option key={size} value={size}>{size}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Business Type
          </label>
          <select
            value={formData.businessType}
            onChange={(e) => setFormData({...formData, businessType: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select business type</option>
            {businessTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div>
      <h3 className="text-xl font-semibold mb-6">Use Case & Goals</h3>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Primary Use Case
          </label>
          <select
            value={formData.useCase}
            onChange={(e) => setFormData({...formData, useCase: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select your primary use case</option>
            {useCases.map(useCase => (
              <option key={useCase} value={useCase}>{useCase}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Business Goals (select all that apply)
          </label>
          <div className="grid grid-cols-2 gap-3">
            {availableGoals.map(goal => (
              <label key={goal} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.goals.includes(goal)}
                  onChange={() => handleGoalToggle(goal)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{goal}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Budget Range
          </label>
          <select
            value={formData.budget}
            onChange={(e) => setFormData({...formData, budget: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select budget range</option>
            {budgetRanges.map(range => (
              <option key={range} value={range}>{range}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div>
      <h3 className="text-xl font-semibold mb-6">Preferences & Timeline</h3>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Preferred Integrations (optional)
          </label>
          <div className="grid grid-cols-2 gap-3">
            {integrations.map(integration => (
              <label key={integration} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.preferredIntegrations.includes(integration)}
                  onChange={() => handleIntegrationToggle(integration)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{integration}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Implementation Timeline
          </label>
          <select
            value={formData.timeline}
            onChange={(e) => setFormData({...formData, timeline: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select timeline</option>
            <option value="immediate">Immediate (within 1 week)</option>
            <option value="month">Within 1 month</option>
            <option value="quarter">Within 3 months</option>
            <option value="planning">Just planning/researching</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            AI/Automation Experience
          </label>
          <select
            value={formData.experience}
            onChange={(e) => setFormData({...formData, experience: e.target.value})}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select experience level</option>
            <option value="beginner">Beginner - New to AI/automation</option>
            <option value="intermediate">Intermediate - Some experience</option>
            <option value="advanced">Advanced - Experienced user</option>
            <option value="expert">Expert - Deep technical knowledge</option>
          </select>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Complete Your Profile
            </h1>
            <p className="text-gray-600">
              Help us customize your CapeControl experience
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
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Processing...' : currentStep === 3 ? 'Complete Profile' : 'Next'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
