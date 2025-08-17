import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { validateEmail, validatePassword, registerUserV2 } from "../api/auth";

// Eye Icon Component for Password Visibility Toggle
function EyeIcon({ isVisible, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
    >
      {isVisible ? (
        // Eye Slash (Hide) Icon
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464m1.414 1.414l.707-.707m0 0L12 12m-1.414-1.414L8.464 8.464m0 0L7.05 7.05m2.828 2.828l-.707.707m12.728-6.363a9.027 9.027 0 01.432 1.644c1.275 4.057-2.965 7-9.543 7a9.97 9.97 0 01-1.725-.15M3 3l18 18" />
        </svg>
      ) : (
        // Eye (Show) Icon
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
      )}
    </button>
  );
}

// View/Info Icon Component for Regular Input Fields
function ViewIcon({ tooltip, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={tooltip}
      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </button>
  );
}

// Registration Status Component
function RegistrationStatus({ status, message }) {
  if (!status) return null;

  const statusConfig = {
    success: {
      bgColor: "bg-green-50",
      borderColor: "border-green-200",
      textColor: "text-green-800",
      icon: (
        <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      )
    },
    error: {
      bgColor: "bg-red-50",
      borderColor: "border-red-200", 
      textColor: "text-red-800",
      icon: (
        <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      )
    },
    info: {
      bgColor: "bg-blue-50",
      borderColor: "border-blue-200",
      textColor: "text-blue-800", 
      icon: (
        <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
      )
    },
    loading: {
      bgColor: "bg-yellow-50",
      borderColor: "border-yellow-200",
      textColor: "text-yellow-800",
      icon: (
        <div className="animate-spin h-5 w-5 border border-yellow-500 rounded-full border-t-transparent"></div>
      )
    }
  };

  const config = statusConfig[status] || statusConfig.info;

  return (
    <div className={`mb-6 p-4 ${config.bgColor} border ${config.borderColor} rounded-lg`}>
      <div className="flex items-center">
        <div className="flex-shrink-0 mr-3">
          {config.icon}
        </div>
        <p className={`text-sm ${config.textColor}`}>{message}</p>
      </div>
    </div>
  );
}

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

// Password Strength Indicator
function PasswordStrengthIndicator({ password }) {
  const calculateStrength = (pwd) => {
    let score = 0;
    if (pwd.length >= 12) score += 25;
    if (/[a-z]/.test(pwd)) score += 25;
    if (/[A-Z]/.test(pwd)) score += 25;
    if (/[0-9]/.test(pwd)) score += 15;
    if (/[^A-Za-z0-9]/.test(pwd)) score += 10;
    return Math.min(score, 100);
  };

  const strength = calculateStrength(password);
  const getStrengthLabel = () => {
    if (strength < 30) return { label: "Weak", color: "bg-red-500" };
    if (strength < 60) return { label: "Fair", color: "bg-yellow-500" };
    if (strength < 80) return { label: "Good", color: "bg-blue-500" };
    return { label: "Strong", color: "bg-green-500" };
  };

  const { label, color } = getStrengthLabel();

  if (!password) return null;

  return (
    <div className="mt-2">
      <div className="flex justify-between text-xs text-gray-600 mb-1">
        <span>Password Strength</span>
        <span>{label}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-1">
        <div 
          className={`h-1 rounded-full transition-all duration-300 ${color}`}
          style={{ width: `${strength}%` }}
        ></div>
      </div>
    </div>
  );
}

// Email Validation Indicator
function EmailValidationIndicator({ email, isValid, isChecking }) {
  if (!email) return null;
  
  return (
    <div className="mt-1 text-xs flex items-center">
      {isChecking ? (
        <>
          <div className="animate-spin h-3 w-3 border border-blue-500 rounded-full border-t-transparent mr-2"></div>
          <span className="text-gray-500">Checking availability...</span>
        </>
      ) : isValid === true ? (
        <>
          <svg className="h-3 w-3 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          <span className="text-green-600">✓ Email available</span>
        </>
      ) : isValid === false ? (
        <>
          <svg className="h-3 w-3 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
          <span className="text-red-600">Email already registered</span>
        </>
      ) : null}
    </div>
  );
}

// Role Selection Card Component
function RoleCard({ role, selectedRole, onSelect }) {
  const isSelected = selectedRole === role;
  const roleData = {
    customer: {
      title: "Customer",
      icon: "👤",
      description: "Access pre-built AI agents to automate business processes. No coding required.",
      features: [
        "Ready-to-use AI agents",
        "Business process automation", 
        "Easy-to-use dashboard",
        "No technical knowledge needed"
      ],
      color: "blue"
    },
    developer: {
      title: "Developer", 
      icon: "👨‍💻",
      description: "Build custom AI agents with developer tools. Earn 30% revenue share.",
      features: [
        "Build custom AI agents",
        "30% revenue sharing",
        "Developer tools & APIs",
        "Marketplace publishing"
      ],
      color: "purple"
    }
  };

  const data = roleData[role];
  const colorClasses = {
    blue: {
      border: isSelected ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-300",
      icon: "text-blue-600",
      title: "text-blue-700",
      features: "text-blue-600"
    },
    purple: {
      border: isSelected ? "border-purple-500 bg-purple-50" : "border-gray-300 hover:border-purple-300", 
      icon: "text-purple-600",
      title: "text-purple-700",
      features: "text-purple-600"
    }
  };

  const colors = colorClasses[data.color];

  return (
    <div
      className={`border-2 rounded-lg p-6 cursor-pointer transition-all ${colors.border}`}
      onClick={() => onSelect(role)}
    >
      <div className="text-center">
        <div className={`text-4xl mb-3 ${colors.icon}`}>
          {data.icon}
        </div>
        <h3 className={`text-xl font-semibold mb-2 ${colors.title}`}>
          {data.title}
        </h3>
        <p className="text-gray-600 text-sm mb-4">
          {data.description}
        </p>
        <ul className="text-left text-sm space-y-1">
          {data.features.map((feature, index) => (
            <li key={index} className={`${colors.features}`}>
              • {feature}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

// Help Support Component
function HelpSupport() {
  return (
    <div className="text-center mt-6">
      <a 
        href="#" 
        className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 transition-colors"
        onClick={(e) => {
          e.preventDefault();
          alert("Support chat would open here. Contact: support@capecontrol.com");
        }}
      >
        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Need Help?
      </a>
    </div>
  );
}

// Step 1: Basic Information + Role Selection (New 2-Step Flow)
function BasicInfoAndRole({ onNext, formData = {}, setFormData }) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [selectedRole, setSelectedRole] = useState("");
  const [error, setError] = useState("");
  
  // Password visibility states
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  // Registration status
  const [registrationStatus, setRegistrationStatus] = useState(null);
  const [registrationMessage, setRegistrationMessage] = useState("");
  
  // Real-time validation states
  const [emailValid, setEmailValid] = useState(null);
  const [emailChecking, setEmailChecking] = useState(false);
  const [passwordMatch, setPasswordMatch] = useState(true);

  // Initialize form data when formData changes
  useEffect(() => {
    if (formData.firstName && formData.firstName !== firstName) setFirstName(formData.firstName);
    if (formData.lastName && formData.lastName !== lastName) setLastName(formData.lastName);
    if (formData.email && formData.email !== email) setEmail(formData.email);
    if (formData.password && formData.password !== password) setPassword(formData.password);
    if (formData.role && formData.role !== selectedRole) setSelectedRole(formData.role);
  }, [formData, firstName, lastName, email, password, selectedRole]); // Include proper dependencies

  // Password validation
  const validatePassword = (pwd) => {
    const requirements = {
      minLength: pwd.length >= 12,
      hasUpper: /[A-Z]/.test(pwd),
      hasLower: /[a-z]/.test(pwd),
      hasNumber: /[0-9]/.test(pwd),
      hasSpecial: /[^A-Za-z0-9]/.test(pwd)
    };
    
    return {
      isValid: Object.values(requirements).every(Boolean),
      requirements
    };
  };

  // Real-time email validation
  useEffect(() => {
    let isMounted = true; // Track if component is mounted
    
    const validateEmailAvailability = async () => {
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        if (isMounted) setEmailValid(null);
        return;
      }

      if (isMounted) setEmailChecking(true);
      try {
        const result = await validateEmail(email);
        if (isMounted) setEmailValid(result.available);
      } catch (error) {
        console.error('Email validation error:', error);
        if (isMounted) setEmailValid(null);
      } finally {
        if (isMounted) setEmailChecking(false);
      }
    };

    const debounce = setTimeout(validateEmailAvailability, 500);
    return () => {
      clearTimeout(debounce);
      isMounted = false; // Mark as unmounted
    };
  }, [email]);

  // Real-time password match validation
  useEffect(() => {
    if (confirmPassword) {
      setPasswordMatch(password === confirmPassword);
    }
  }, [password, confirmPassword]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setRegistrationStatus("loading");
    setRegistrationMessage("Validating information...");

    // Enhanced validation
    if (!firstName.trim() || !lastName.trim()) {
      setError("First and last name are required");
      setRegistrationStatus("error");
      setRegistrationMessage("Please fill in all required fields");
      return;
    }

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Please enter a valid email address");
      setRegistrationStatus("error");
      setRegistrationMessage("Invalid email format");
      return;
    }

    if (emailValid === false) {
      setError("This email is already registered. Try logging in or use a different email.");
      setRegistrationStatus("error");
      setRegistrationMessage("Email already exists");
      return;
    }

    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
      setError("Password must be at least 12 characters with uppercase, lowercase, number, and special character");
      setRegistrationStatus("error");
      setRegistrationMessage("Password does not meet requirements");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      setRegistrationStatus("error");
      setRegistrationMessage("Password confirmation failed");
      return;
    }

    if (!selectedRole) {
      setError("Please select your role");
      setRegistrationStatus("error");
      setRegistrationMessage("Role selection required");
      return;
    }

    setRegistrationStatus("success");
    setRegistrationMessage("Basic information validated successfully! Proceeding to next step...");

    // Update form data and proceed to next step
    const updatedFormData = {
      ...formData,
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      email: email.trim().toLowerCase(),
      password,
      role: selectedRole,
    };
    
    setFormData(updatedFormData);

    // Small delay to show success message
    setTimeout(() => {
      onNext();
    }, 1000);
  };

  const passwordValidation = validatePassword(password);

  return (
    <div className="container-mobile mt-8 lg:mt-10">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Header with gradient background */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-8 sm:px-8 lg:px-12">
          <div className="text-center">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white mb-2">
              Create Your CapeControl Account
            </h2>
            <p className="text-blue-100 text-base lg:text-lg">
              Step 1: Basic Information & Role Selection
            </p>
            <div className="mt-6">
              <ProgressBar currentStep={1} totalSteps={2} />
            </div>
          </div>
        </div>
        
        {/* Main content */}
        <div className="p-6 sm:p-8 lg:p-12">

          <RegistrationStatus status={registrationStatus} message={registrationMessage} />

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-400 rounded-lg">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-red-700 text-sm font-medium">{error}</p>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Personal Information */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 lg:p-8 rounded-xl border border-blue-100">
              <div className="flex items-center mb-6">
                <div className="bg-blue-600 rounded-full p-2 mr-3">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900">Personal Information</h3>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    First Name *
                  </label>
                  <div className="relative">
                    <input
                      type="text" 
                      autoComplete="given-name"
                      className="input-mobile border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 shadow-sm"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      placeholder="Enter your first name"
                      required
                    />
                    <ViewIcon 
                      tooltip="Your first name for personalization" 
                      onClick={() => alert("We'll use your first name to personalize your experience.")} 
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Last Name *
                  </label>
                  <div className="relative">
                    <input
                      type="text" 
                      autoComplete="family-name"
                      className="input-mobile border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 shadow-sm"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      placeholder="Enter your last name"
                      required
                    />
                    <ViewIcon 
                      tooltip="Your last name for formal communications" 
                      onClick={() => alert("Your last name will be used for formal communications and certificates.")} 
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Account Information */}
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-6 lg:p-8 rounded-xl border border-purple-100">
              <div className="flex items-center mb-6">
                <div className="bg-purple-600 rounded-full p-2 mr-3">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m0 0a2 2 0 012 2v6a2 2 0 01-2 2h-10a2 2 0 01-2-2V9a2 2 0 012-2m0 0V7a2 2 0 012-2h4z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-900">Account Information</h3>
              </div>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <div className="relative">
                    <input
                      type="email" 
                      autoComplete="email"
                      className="input-mobile border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 shadow-sm"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email address"
                      required
                    />
                    <ViewIcon 
                      tooltip="We'll use this email for login and notifications" 
                      onClick={() => alert("This email will be your login username and used for important notifications.")} 
                    />
                  </div>
                  <EmailValidationIndicator 
                    email={email} 
                    isValid={emailValid} 
                    isChecking={emailChecking} 
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Password *
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"} 
                      autoComplete="new-password"
                      className="input-mobile border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 shadow-sm"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Create a strong password"
                      minLength={12}
                      required
                    />
                    <EyeIcon 
                      isVisible={showPassword} 
                      onClick={() => setShowPassword(!showPassword)} 
                    />
                  </div>
                  <PasswordStrengthIndicator password={password} />
                  {password && (
                    <div className="mt-3 p-3 bg-white rounded-lg border border-gray-200">
                      <p className="font-semibold text-sm text-gray-700 mb-2">Password Requirements:</p>
                  <ul className="mt-1 space-y-1">
                    <li className={passwordValidation.requirements.minLength ? 'text-green-600' : 'text-red-600'}>
                      ✓ At least 12 characters
                    </li>
                    <li className={passwordValidation.requirements.hasUpper ? 'text-green-600' : 'text-red-600'}>
                      ✓ One uppercase letter
                    </li>
                    <li className={passwordValidation.requirements.hasLower ? 'text-green-600' : 'text-red-600'}>
                      ✓ One lowercase letter
                    </li>
                    <li className={passwordValidation.requirements.hasNumber ? 'text-green-600' : 'text-red-600'}>
                      ✓ One number
                    </li>
                    <li className={passwordValidation.requirements.hasSpecial ? 'text-green-600' : 'text-red-600'}>
                      ✓ One special character
                    </li>
                  </ul>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm Password *
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? "text" : "password"} 
                  autoComplete="new-password"
                  className={`w-full p-3 pr-12 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    confirmPassword && !passwordMatch ? 'border-red-300' : 'border-gray-300'
                  }`}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  required
                />
                <EyeIcon 
                  isVisible={showConfirmPassword} 
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)} 
                />
              </div>
              {confirmPassword && !passwordMatch && (
                <p className="mt-1 text-xs text-red-600">Passwords do not match</p>
              )}
              {confirmPassword && passwordMatch && (
                <p className="mt-1 text-xs text-green-600">Passwords match ✓</p>
              )}
            </div>
          </div>
        </div>

        {/* Role Selection */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Choose Your Role</h3>
          <p className="text-gray-600 mb-6">Select how you'll use CapeControl to get personalized features</p>
          
          <div className="grid md:grid-cols-2 gap-6">
            <RoleCard 
              role="customer" 
              selectedRole={selectedRole} 
              onSelect={setSelectedRole} 
            />
            <RoleCard 
              role="developer" 
              selectedRole={selectedRole} 
              onSelect={setSelectedRole} 
            />
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-6">
          <button
            type="submit"
            className="w-full bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
            disabled={emailChecking || !passwordMatch || !passwordValidation.isValid || !selectedRole}
          >
            {emailChecking ? "Checking email..." : "Continue to Details →"}
          </button>
          
          {(!passwordValidation.isValid || !passwordMatch || !selectedRole) && (
            <p className="text-center text-xs text-gray-500 mt-2">
              {!passwordValidation.isValid && "Complete password requirements, "}
              {!passwordMatch && "confirm password, "}
              {!selectedRole && "select your role "}
              to continue
            </p>
          )}
        </div>

        <p className="text-center text-sm text-gray-600 mt-4">
          Already have an account?{" "}
          <a href="/login-customer" className="text-blue-600 hover:underline">
            Sign in
          </a>
        </p>
      </form>
      
      <HelpSupport />
    </div>
      </div>
    </div>
  );
}

// Step 2: Detailed Information (Role-specific)
function DetailedInformation({ formData = {}, setFormData, onSubmit }) {
  const [company, setCompany] = useState("");
  const [phone, setPhone] = useState("");
  const [website, setWebsite] = useState("");
  const [experience, setExperience] = useState("");
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Registration status
  const [registrationStatus, setRegistrationStatus] = useState(null);
  const [registrationMessage, setRegistrationMessage] = useState("");

  // Initialize form data when formData changes
  useEffect(() => {
    if (formData.company && formData.company !== company) setCompany(formData.company);
    if (formData.phone && formData.phone !== phone) setPhone(formData.phone);
    if (formData.website && formData.website !== website) setWebsite(formData.website);
    if (formData.experience && formData.experience !== experience) setExperience(formData.experience);
  }, [formData, company, phone, website, experience]); // Include proper dependencies

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!agreedToTerms) {
      setError("You must agree to the Terms & Conditions");
      setRegistrationStatus("error");
      setRegistrationMessage("Terms and conditions must be accepted");
      return;
    }

    if (!company.trim()) {
      setError("Company/Organization name is required");
      setRegistrationStatus("error");
      setRegistrationMessage("Company information is required");
      return;
    }

    setLoading(true);
    setError("");
    setRegistrationStatus("loading");
    setRegistrationMessage("Creating your account...");

    const finalData = {
      ...formData,
      company: company.trim(),
      phone: phone.trim(),
      website: website.trim(),
      experience,
    };

    try {
      setRegistrationMessage("Processing registration...");
      await onSubmit(finalData);
      setRegistrationStatus("success");
      setRegistrationMessage("Account created successfully! Redirecting...");
    } catch (err) {
      setError(err.message);
      setRegistrationStatus("error");
      setRegistrationMessage("Registration failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-mobile mt-8 lg:mt-10">
      <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Header with gradient background */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-8 sm:px-8 lg:px-12">
          <div className="text-center">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white mb-2">
              Complete Your Profile
            </h2>
            <p className="text-purple-100 text-base lg:text-lg">
              Step 2: {formData.role === "customer" ? "Business" : "Developer"} Details
            </p>
            <div className="mt-6">
              <ProgressBar currentStep={2} totalSteps={2} />
            </div>
          </div>
        </div>
        
        {/* Main content */}
        <div className="p-6 sm:p-8 lg:p-12">
          <RegistrationStatus status={registrationStatus} message={registrationMessage} />

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-400 rounded-lg">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-red-700 text-sm font-medium">{error}</p>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Business/Developer Information */}
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-6 lg:p-8 rounded-xl border border-purple-100">
              <div className="flex items-center mb-6">
                <div className="bg-purple-600 rounded-full p-2 mr-3">
                  {formData.role === "customer" ? (
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-2m-2 0H7m5 0v-5a2 2 0 00-2-2H8a2 2 0 00-2 2v5m5 0v-3a1 1 0 00-1-1h-1a1 1 0 00-1 1v3m4 0h2M7 7h3v3H7V7z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                  )}
                </div>
                <h3 className="text-xl font-bold text-gray-900">
                  {formData.role === "customer" ? "Business Information" : "Developer Information"}
                </h3>
              </div>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {formData.role === "customer" ? "Company Name" : "Developer/Company Name"} *
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      autoComplete="organization"
                      className="input-mobile border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 shadow-sm"
                      value={company}
                      onChange={(e) => setCompany(e.target.value)}
                      placeholder={formData.role === "customer" ? "Your company name" : "Your name or company"}
                      required
                    />
                    <ViewIcon 
                      tooltip={formData.role === "customer" ? "Your business/company name" : "Your professional name or company"} 
                      onClick={() => alert(formData.role === "customer" ? "Enter your business or company name." : "Enter your professional name or development company.")} 
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Phone Number (Optional)
                  </label>
                  <div className="relative">
                    <input
                      type="tel"
                      autoComplete="tel"
                      className="input-mobile border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 shadow-sm"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="+1 (555) 123-4567"
                    />
                    <ViewIcon 
                      tooltip="Optional phone number for support contact" 
                      onClick={() => alert("Phone number is optional and will only be used for important support communications.")} 
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Website (Optional)
                  </label>
                  <div className="relative">
                    <input
                      type="url"
                      autoComplete="url"
                      className="input-mobile border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 shadow-sm"
                      value={website}
                      onChange={(e) => setWebsite(e.target.value)}
                      placeholder="https://your-website.com"
                    />
                    <ViewIcon 
                      tooltip="Your business or portfolio website" 
                      onClick={() => alert("Add your business website or portfolio URL to showcase your work.")} 
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {formData.role === "customer" ? "Business Experience" : "Development Experience"} *
                  </label>
                  <select
                    className="input-mobile border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 shadow-sm"
                    value={experience}
                    onChange={(e) => setExperience(e.target.value)}
                    required
                  >
                    <option value="">Select experience level</option>
                    <option value="beginner">Beginner (0-1 years)</option>
                    <option value="intermediate">Intermediate (2-5 years)</option>
                    <option value="advanced">Advanced (5+ years)</option>
                    <option value="expert">Expert (10+ years)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Terms Agreement */}
            <div className="bg-gradient-to-br from-gray-50 to-blue-50 p-6 lg:p-8 rounded-xl border border-gray-200">
              <div className="flex items-start space-x-4">
                <input
                  type="checkbox"
                  id="terms"
                  className="mt-1 h-5 w-5 text-purple-600 focus:ring-purple-500 border-gray-300 rounded transition-colors"
                  checked={agreedToTerms}
                  onChange={(e) => setAgreedToTerms(e.target.checked)}
                />
                <label htmlFor="terms" className="text-sm text-gray-700 leading-relaxed">
                  I agree to the{" "}
                  <a href="/terms" className="text-purple-600 hover:text-purple-700 underline font-medium" target="_blank" rel="noopener noreferrer">
                    Terms & Conditions
                  </a>{" "}
                  and{" "}
                  <a href="/privacy" className="text-purple-600 hover:text-purple-700 underline font-medium" target="_blank" rel="noopener noreferrer">
                    Privacy Policy
                  </a>{" "}
                  for {formData.role === "customer" ? "Business Users" : "Developers"}
                </label>
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-6">
              <button
                type="submit"
                disabled={loading || !agreedToTerms}
                className="btn-mobile-lg w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-xl shadow-lg hover:from-purple-700 hover:to-blue-700 active:scale-95 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-purple-600 disabled:hover:to-blue-600"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating Account...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    Create My Account
                    <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </span>
                )}
              </button>
              
              {!agreedToTerms && (
                <p className="text-center text-sm text-gray-500 mt-3">
                  Please agree to the terms and conditions to continue
                </p>
              )}
            </div>

            <p className="text-center text-sm text-gray-600 mt-6">
              Need help?{" "}
              <a href="/support" className="text-purple-600 hover:underline font-medium">
                Contact Support
              </a>
            </p>
          </form>
      
      <HelpSupport />
        </div>
      </div>
    </div>
  );
}

// Main Registration Component (New 2-Step Flow)
export default function Register() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({});
  const navigate = useNavigate();

  const handleNext = () => {
    setCurrentStep(currentStep + 1);
  };

  const handleSubmit = async (finalData) => {
    try {
      const userData = await registerUserV2(finalData);

      // Registration successful - redirect to Phase 2 based on role
      if (finalData.role === "customer") {
        navigate("/phase2-customer", { 
          state: { userData: { ...finalData, ...userData } }
        });
      } else {
        navigate("/phase2-developer", { 
          state: { userData: { ...finalData, ...userData } }
        });
      }
    } catch (err) {
      throw err;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      {currentStep === 1 && (
        <BasicInfoAndRole
          onNext={handleNext}
          formData={formData}
          setFormData={setFormData}
        />
      )}
      {currentStep === 2 && (
        <DetailedInformation
          formData={formData}
          setFormData={setFormData}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  );
}
