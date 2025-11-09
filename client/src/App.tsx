import { BrowserRouter, Route, Routes } from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import SocialCallback from "./pages/SocialCallback";
import OnboardingCustomer from "./pages/onboarding/Customer";
import OnboardingDeveloper from "./pages/onboarding/Developer";
import VerifyEmail from "./pages/VerifyEmail";
import LogoTestPage from "./pages/LogoTestPage";

// New pages based on sitemap
import Dashboard from "./pages/Dashboard";
import Welcome from "./pages/Welcome";
import OnboardingGuide from "./pages/onboarding/OnboardingGuide";
import OnboardingChecklist from "./pages/onboarding/OnboardingChecklist";
import OnboardingProfile from "./pages/onboarding/OnboardingProfile";
import About from "./pages/About";
import Subscribe from "./pages/Subscribe";

// CapeControl Auth Components (Production)
import LoginPage from "./components/Auth/LoginPage";
import MFAChallenge from "./components/Auth/MFAChallenge"; 
import MFAEnroll from "./components/Auth/MFAEnroll";

const App = () => (
  <BrowserRouter
    future={{
      v7_startTransition: true,
      v7_relativeSplatPath: true,
    }}
  >
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/auth/callback" element={<SocialCallback />} />
      <Route path="/onboarding/customer" element={<OnboardingCustomer />} />
      <Route path="/onboarding/developer" element={<OnboardingDeveloper />} />
      <Route path="/verify-email/:token" element={<VerifyEmail />} />
      
      {/* New pages based on sitemap */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/welcome" element={<Welcome />} />
      <Route path="/onboarding/guide" element={<OnboardingGuide />} />
      <Route path="/onboarding/checklist" element={<OnboardingChecklist />} />
      <Route path="/onboarding/profile" element={<OnboardingProfile />} />
      <Route path="/about" element={<About />} />
      <Route path="/subscribe" element={<Subscribe />} />
      
      {/* CapeControl Auth Routes - Production Ready */}
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/mfa" element={<MFAChallenge onSuccess={() => console.log('MFA Success')} />} />
      <Route path="/account/mfa-enroll" element={<MFAEnroll />} />
      <Route path="/test/logo" element={<LogoTestPage />} />
    </Routes>
  </BrowserRouter>
);

export default App;
