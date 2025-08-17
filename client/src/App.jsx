import { Routes, Route, Navigate } from "react-router-dom";
import { Suspense, lazy } from "react";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import CapeAISystemSaferWrapper from "./components/CapeAISystemSaferWrapper";

// ✅ Lazy-loaded pages
const Landing = lazy(() => import("./pages/Landing"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/RegisterV2"));
const RegisterLegacy = lazy(() => import("./pages/Register"));
const Phase2CustomerRegistration = lazy(() => import("./pages/Phase2CustomerRegistration"));
const Phase2DeveloperRegistration = lazy(() => import("./pages/Phase2DeveloperRegistration"));
const LoginCustomer = lazy(() => import("./pages/LoginCustomer"));
const LoginDeveloper = lazy(() => import("./pages/LoginDeveloper"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const UserDashboard = lazy(() => import("./pages/UserDashboard"));
const DeveloperDashboard = lazy(() => import("./pages/DeveloperDashboard"));
const PerformanceDashboard = lazy(() => import("./pages/PerformanceDashboardPage"));
const AnalyticsDashboard = lazy(() => import("./pages/AnalyticsDashboardPage"));
const PersonalizedDashboard = lazy(() => import("./components/PersonalizedDashboard"));
const HealthDashboard = lazy(() => import("./pages/HealthDashboard"));
const Logout = lazy(() => import("./pages/Logout"));
const HowItWorks = lazy(() => import("./pages/HowItWorks"));
const HowItWorksUser = lazy(() => import("./pages/HowItWorksUser"));
const HowItWorksDeveloper = lazy(() => import("./pages/HowItWorksDeveloper"));
const Vision = lazy(() => import("./pages/Vision"));
const Platform = lazy(() => import("./pages/Platform"));
const Developers = lazy(() => import("./pages/Developers"));
const About = lazy(() => import("./pages/About"));
const Privacy = lazy(() => import("./pages/Privacy"));
const Terms = lazy(() => import("./pages/Terms"));
const DeveloperTerms = lazy(() => import("./pages/DeveloperTerms"));
const Subscribe = lazy(() => import("./components/Subscribe"));
const Credits = lazy(() => import("./components/Credits"));
const ForgotPassword = lazy(() => import("./pages/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/ResetPassword"));
const ProtectedRoute = lazy(() => import("./components/ProtectedRoute"));

// PayFast redirects
const PayFastReturn = lazy(() => import("./pages/PayFastReturn"));
const PayFastCancel = lazy(() => import("./pages/PayFastCancel"));

export default function App() {
  return (
    <div className="min-h-screen flex flex-col font-sans bg-white text-gray-900 dark:bg-gray-900 dark:text-white">
      <Navbar />
      <main className="flex-1 pt-20">
          <Suspense
            fallback={
              <div className="flex items-center justify-center min-h-[50vh]" role="status">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mx-auto"></div>
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading...</p>
                </div>
              </div>
            }
          >
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/vision" element={<Vision />} />
              <Route path="/platform" element={<Platform />} />
              <Route path="/developers" element={<Developers />} />
              <Route path="/about" element={<About />} />
              <Route path="/privacy" element={<Privacy />} />
              <Route path="/terms" element={<Terms />} />
              <Route path="/developer-terms" element={<DeveloperTerms />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/register-legacy" element={<RegisterLegacy />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/phase2-customer" element={<Phase2CustomerRegistration />} />
              <Route path="/phase2-developer" element={<Phase2DeveloperRegistration />} />
              <Route path="/login-customer" element={<LoginCustomer />} />
              <Route path="/login-developer" element={<LoginDeveloper />} />
              <Route path="/logout" element={<Logout />} />
              <Route path="/how-it-works" element={<HowItWorks />} />
              <Route path="/how-it-works-user" element={<HowItWorksUser />} />
              <Route path="/how-it-works-developer" element={<HowItWorksDeveloper />} />
              <Route path="/subscribe" element={<Subscribe />} />
              <Route
                path="/credits"
                element={
                  <ProtectedRoute>
                    <Credits />
                  </ProtectedRoute>
                }
              />
              {/* PayFast return/cancel */}
              <Route path="/payfast/return" element={<PayFastReturn />} />
              <Route path="/payfast/cancel" element={<PayFastCancel />} />
              
              {/* Dashboard Routes with Role-Based Protection */}
              <Route path="/profile" element={<Navigate to="/dashboard" replace />} />
              <Route path="/settings" element={<Navigate to="/dashboard" replace />} />
              
              {/* Health Dashboard - System Monitoring */}
              <Route
                path="/health"
                element={
                  <ProtectedRoute>
                    <HealthDashboard />
                  </ProtectedRoute>
                }
              />
              
              {/* Main Dashboard - Auto-redirects to role-specific dashboard */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              
              {/* Customer/Business User Dashboard */}
              <Route
                path="/dashboard/user"
                element={
                  <ProtectedRoute requiredRole="customer">
                    <UserDashboard />
                  </ProtectedRoute>
                }
              />
              
              {/* Developer Dashboard */}
              <Route
                path="/dashboard/developer"
                element={
                  <ProtectedRoute requiredRole="developer">
                    <DeveloperDashboard />
                  </ProtectedRoute>
                }
              />
              
              {/* Admin/Performance Dashboard */}
              <Route
                path="/dashboard/performance"
                element={
                  <ProtectedRoute requiredRole="admin">
                    <PerformanceDashboard />
                  </ProtectedRoute>
                }
              />
              
              {/* Analytics Dashboard */}
              <Route
                path="/dashboard/analytics"
                element={
                  <ProtectedRoute requiredRole="admin">
                    <AnalyticsDashboard />
                  </ProtectedRoute>
                }
              />
              
              {/* Personalized Dashboard Demo */}
              <Route
                path="/dashboard/personalized"
                element={
                  <ProtectedRoute>
                    <PersonalizedDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="*"
                element={
                  <div className="p-4 text-center text-red-600">
                    404 - Page Not Found
                  </div>
                }
              />
            </Routes>
          </Suspense>
        </main>
        <Footer />
        <CapeAISystemSaferWrapper />
      </div>
  );
}
