import useCapeAISafe from '../../hooks/useCapeAISafe';

export default function OnboardingChecklist() {
  const { onboardingData, addMessage, toggleVisibility } = useCapeAISafe();

  const checklist = [
    { 
      id: 'profile',
      label: "✅ Set up your profile", 
      done: onboardingData.profileComplete || false,
      helpText: "Complete your business profile to get personalized AI recommendations"
    },
    { 
      id: 'features',
      label: "📄 Review the platform features", 
      done: onboardingData.featuresViewed || false,
      helpText: "Learn about our AI agents and how they can help your business"
    },
    { 
      id: 'assistant',
      label: "🤖 Meet your AI assistant", 
      done: onboardingData.aiIntroduced || false,
      helpText: "Chat with CapeAI to get personalized guidance and support"
    },
    { 
      id: 'dashboard',
      label: "📈 View your dashboard", 
      done: onboardingData.dashboardTour || false,
      helpText: "Explore your control center for managing AI agents and analytics"
    },
    { 
      id: 'agent',
      label: "🚀 Launch your first agent", 
      done: onboardingData.firstAgentLaunched || false,
      helpText: "Try out an AI agent to see the platform in action"
    },
  ];

  const handleItemClick = (item) => {
    const helpMessages = {
      'profile': 'Let me help you set up your profile! What type of business are you running?',
      'features': 'I\'d love to show you our platform features! Which area interests you most: automation, content creation, or data analysis?',
      'assistant': 'Hi there! I\'m CapeAI, and I\'m here to help you succeed on our platform. What questions do you have?',
      'dashboard': 'Your dashboard is powerful! Let me give you a quick tour of the key features.',
      'agent': 'Ready to launch your first AI agent? I can recommend the best one based on your needs!'
    };

    addMessage('assistant', helpMessages[item.id]);
    toggleVisibility(); // Open the chat
  };

  const completedCount = checklist.filter(item => item.done).length;
  const progressPercentage = (completedCount / checklist.length) * 100;

  return (
    <div className="bg-white p-6 rounded-lg shadow mt-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Getting Started Checklist</h3>
        <div className="text-sm text-gray-600">
          {completedCount}/{checklist.length} completed
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
        <div 
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>

      <ul className="space-y-3">
        {checklist.map((item, index) => (
          <li
            key={index}
            className={`flex items-start gap-3 p-3 rounded-lg border transition-colors cursor-pointer hover:bg-gray-50 ${
              item.done ? "bg-green-50 border-green-200" : "bg-gray-50 border-gray-200"
            }`}
            onClick={() => handleItemClick(item)}
          >
            <span className="text-xl mt-0.5">
              {item.done ? "✅" : "⬜"}
            </span>
            <div className="flex-1">
              <div className={`font-medium ${item.done ? "text-green-700" : "text-gray-800"}`}>
                {item.label}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {item.helpText}
              </div>
            </div>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              Get Help
            </button>
          </li>
        ))}
      </ul>

      {progressPercentage === 100 && (
        <div className="mt-4 p-4 bg-green-100 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 text-green-700">
            <span className="text-xl">🎉</span>
            <span className="font-semibold">Congratulations!</span>
          </div>
          <p className="text-sm text-green-600 mt-1">
            You've completed the onboarding process. You're ready to explore the full power of CapeControl!
          </p>
        </div>
      )}
    </div>
  );
}
