import { useState, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import { loginUserV2 } from "../api/auth";
import { setToken } from "../utils/token";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loginTiming, setLoginTiming] = useState(null);
  
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const validateForm = useCallback(() => {
    const newErrors = {};
    
    if (!email) {
      newErrors.email = "email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "invalid email format";
    }
    
    if (!password) {
      newErrors.password = "password is required";
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }
    
    return newErrors;
  }, [email, password]);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    
    // Inline validation to avoid dependency issues
    const newErrors = {};
    
    if (!email) {
      newErrors.email = "email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "invalid email format";
    }
    
    if (!password) {
      newErrors.password = "password is required";
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Clear errors and start timing
    setErrors({});
    setError(null);
    setIsLoading(true);
    setLoginTiming(null);
    
    const startTime = performance.now();
    
    try {
      console.log(`🚀 Login attempt started at ${new Date().toISOString()}`);
      const result = await loginUserV2(email, password);
      const endTime = performance.now();
      const duration = Math.round(endTime - startTime);
      
      setLoginTiming(duration);
      console.log(`✅ Login successful in ${duration}ms`);
      
      // Store token and user data
      setToken(result.access_token);
      setUser(result.user);
      
      // Navigate to dashboard or desired page
      navigate('/dashboard');
    } catch (err) {
      const endTime = performance.now();
      const duration = Math.round(endTime - startTime);
      
      setLoginTiming(duration);
      console.log(`❌ Login failed in ${duration}ms: ${err.message}`);
      setError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  }, [email, password, setUser, navigate]);

  const handleEmailChange = useCallback((e) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    // Clear error without dependency on errors object
    setErrors(prev => prev.email ? { ...prev, email: '' } : prev);
  }, []);

  const handlePasswordChange = useCallback((e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    // Clear error without dependency on errors object
    setErrors(prev => prev.password ? { ...prev, password: '' } : prev);
  }, []);

  const toggleShowPassword = useCallback(() => {
    setShowPassword(prev => !prev);
  }, []);

  const handleSocialLogin = useCallback((provider) => {
    // Placeholder for social login
    console.log(`Social login with ${provider}`);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-2xl p-6 sm:p-8 border border-gray-100">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Login</h1>
            <p className="text-gray-600">Sign in to your account</p>
          </div>
          
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-red-800 text-sm font-medium" role="alert">
                {error}
                {loginTiming && (
                  <div className="text-red-600 text-xs mt-1">
                    Request took {loginTiming}ms
                  </div>
                )}
              </div>
            </div>
          )}

          {loginTiming && !error && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-green-800 text-sm font-medium">
                Login successful in {loginTiming}ms
              </div>
            </div>
          )}
          
          <form onSubmit={handleSubmit} role="form" aria-labelledby="login-heading" className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                className={`input-mobile ${errors.email ? 'border-red-500' : ''}`}
                type="email" 
                autoComplete="username"
                placeholder="Enter your email"
                value={email}
                onChange={handleEmailChange}
                aria-describedby={errors.email ? "email-error" : undefined}
                disabled={isLoading}
              />
              {errors.email && (
                <div id="email-error" className="text-red-600 text-sm mt-1" role="alert">
                  {errors.email}
                </div>
              )}
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  className={`input-mobile pr-10 ${errors.password ? 'border-red-500' : ''}`}
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={handlePasswordChange}
                  aria-describedby={errors.password ? "password-error" : undefined}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={toggleShowPassword}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  data-testid="password-toggle"
                  tabIndex={-1}
                >
                  <span className="text-gray-400 hover:text-gray-600">
                    {showPassword ? "�" : "👁"}
                  </span>
                </button>
              </div>
              {errors.password && (
                <div id="password-error" className="text-red-600 text-sm mt-1" role="alert">
                  {errors.password}
                </div>
              )}
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center">
              <input
                id="remember-me"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700">
                Remember me
              </label>
            </div>
            
            <button
              className="btn-mobile-lg w-full bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all duration-200"
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full mr-3"></div>
                  <span>Logging in...</span>
                  {loginTiming && (
                    <span className="ml-2 text-xs opacity-75">
                      ({Math.round(performance.now() - loginTiming)}ms)
                    </span>
                  )}
                </div>
              ) : "Login"}
            </button>
          </form>

          {/* Social Login */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                onClick={() => handleSocialLogin('google')}
              >
                Continue with Google
              </button>
              <button
                type="button"
                className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                onClick={() => handleSocialLogin('github')}
              >
                Continue with GitHub
              </button>
            </div>
          </div>
          
          <div className="mt-8 text-center">
            <div className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500 transition-colors">
                Sign up
              </Link>
            </div>
            <div className="mt-2">
              <Link to="/forgot-password" className="text-sm text-blue-600 hover:text-blue-500 transition-colors">
                Forgot password?
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
