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
import FigmaDemo from "./pages/FigmaDemo";
import TestPage from "./pages/TestPage";
import Demo1Demo from "./pages/Demo1Demo";
import MainPageDemo from "./pages/MainPageDemo";

// CapeCraft Components
import HomePage from "./pages/HomePage";
import SubscribePage from "./pages/SubscribePage";
import AboutPage from "./pages/AboutPage";
import CapeRegisterPage from "./pages/CapeRegisterPage";
import CapeLoginPage from "./pages/CapeLoginPage";
import { ResetPasswordPage } from "./components/generated/ResetPasswordPage";

// CapeControl Auth Components
import LoginPage from "./components/Auth/LoginPage";
import MFAChallenge from "./components/Auth/MFAChallenge"; 
import MFAEnroll from "./components/Auth/MFAEnroll";
import LogoTestPage from "./pages/LogoTestPage";

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
      <Route path="/figma-demo" element={<FigmaDemo />} />
      <Route path="/test" element={<TestPage />} />
      <Route path="/demo1-demo" element={<Demo1Demo />} />
      <Route path="/mainpage-demo" element={<MainPageDemo />} />
      
      {/* CapeCraft Routes - Based on MindMup Design */}
      <Route path="/capecraft" element={<HomePage />} />
      <Route path="/capecraft/subscribe" element={<SubscribePage />} />
      <Route path="/capecraft/about" element={<AboutPage />} />
      <Route path="/capecraft/register" element={<CapeRegisterPage />} />
      <Route path="/capecraft/login" element={<CapeLoginPage />} />
      <Route path="/capecraft/reset-password" element={<ResetPasswordPage />} />
      
      {/* CapeControl Auth Routes - DOCS251107 Implementation */}
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/mfa" element={<MFAChallenge onSuccess={() => console.log('MFA Success')} />} />
      <Route path="/account/mfa-enroll" element={<MFAEnroll />} />
      <Route path="/test/logo" element={<LogoTestPage />} />
    </Routes>
  </BrowserRouter>
);

export default App;
