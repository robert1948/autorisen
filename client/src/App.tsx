import React from "react";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";

import { features } from "./config/features";

// Public
import HomePage from "./pages/HomePage";
import Welcome from "./pages/Welcome";
import About from "./pages/About";
import Subscribe from "./pages/Subscribe";

// Auth pages / flows
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import SocialCallback from "./pages/SocialCallback";
import VerifyEmail from "./pages/VerifyEmail";

// Onboarding pages
import OnboardingCustomer from "./pages/onboarding/Customer";
import OnboardingDeveloper from "./pages/onboarding/Developer";
import OnboardingGuide from "./pages/onboarding/OnboardingGuide";
import OnboardingChecklist from "./pages/onboarding/OnboardingChecklist";
import OnboardingProfile from "./pages/onboarding/OnboardingProfile";

// App pages
import Dashboard from "./pages/Dashboard";
import Marketplace from "./pages/Marketplace";
import Agents from "./pages/Agents";
import Settings from "./pages/Settings";
import Billing from "./pages/Billing";
import Checkout from "./pages/Checkout";
import CheckoutSuccess from "./pages/CheckoutSuccess";
import CheckoutCancel from "./pages/CheckoutCancel";
import ChatConsole from "./pages/ChatConsole";
import LogoTestPage from "./pages/LogoTestPage";
import SunbirdPilotMobile from "./pages/sunbird/SunbirdPilotMobile";

// CapeControl auth components (production-ready)
import LoginPage from "./components/Auth/LoginPage";
import MFAChallenge from "./components/Auth/MFAChallenge";
import MFAEnroll from "./components/Auth/MFAEnroll";

// Canonical app entry redirect
import AppEntryRedirect from "./routes/AppEntryRedirect";

/**
 * Redirect legacy /verify-email/:token → /auth/verify-email/:token
 */
function VerifyEmailRedirect() {
  const { token } = useParams();
  return <Navigate to={`/auth/verify-email/${token ?? ""}`} replace />;
}

/**
 * Redirect legacy /chat/:threadId → /app/chat/:threadId
 */
function ChatThreadRedirect() {
  const { threadId } = useParams();
  return <Navigate to={`/app/chat/${threadId ?? ""}`} replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* -------------------- PUBLIC -------------------- */}
        <Route path="/" element={<HomePage />} />
        <Route path="/demo" element={<Welcome />} />
        <Route path="/how-it-works" element={<About />} />
        <Route path="/about" element={<About />} />
        <Route path="/subscribe" element={<Subscribe />} />

        {/* -------------------- AUTH (CANONICAL) -------------------- */}
        <Route path="/auth/login" element={<LoginPage />} />
        <Route path="/auth/register" element={<Register />} />
        <Route path="/auth/forgot-password" element={<ForgotPassword />} />
        <Route path="/auth/reset-password" element={<ResetPassword />} />
        <Route path="/auth/callback" element={<SocialCallback />} />
        <Route path="/auth/verify-email/:token" element={<VerifyEmail />} />

        {/* MFA */}
        <Route
          path="/auth/mfa"
          element={<MFAChallenge onSuccess={() => console.log("MFA Success")} />}
        />
        <Route path="/account/mfa-enroll" element={<MFAEnroll />} />

        {/* -------------------- LEGACY AUTH ALIASES -------------------- */}
        <Route path="/login" element={<Navigate to="/auth/login" replace />} />
        <Route path="/signup" element={<Navigate to="/auth/register" replace />} />
        <Route path="/register" element={<Navigate to="/auth/register" replace />} />
        <Route path="/forgot-password" element={<Navigate to="/auth/forgot-password" replace />} />
        <Route path="/reset-password" element={<Navigate to="/auth/reset-password" replace />} />
        <Route path="/verify-email/:token" element={<VerifyEmailRedirect />} />

        {/* -------------------- APP (CANONICAL) -------------------- */}
        <Route path="/app" element={<AppEntryRedirect />} />

        {/* Onboarding canonical entry */}
        {features.onboarding && (
          <>
            <Route path="/app/onboarding" element={<OnboardingGuide />} />
            <Route path="/app/onboarding/checklist" element={<OnboardingChecklist />} />
            <Route path="/app/onboarding/profile" element={<OnboardingProfile />} />
            <Route path="/app/onboarding/customer" element={<OnboardingCustomer />} />
            <Route path="/app/onboarding/developer" element={<OnboardingDeveloper />} />
          </>
        )}

        {/* Core app pages */}
        <Route path="/app/dashboard" element={<Dashboard />} />
        <Route path="/app/settings" element={<Settings />} />

        {features.sunbirdPilot && (
          <Route path="/app/sunbird-pilot" element={<SunbirdPilotMobile />} />
        )}

        {features.agentsShell && (
          <>
            <Route path="/app/agents" element={<Agents />} />
            <Route path="/app/chat" element={<ChatConsole />} />
            <Route path="/app/chat/:threadId" element={<ChatConsole />} />
          </>
        )}

        {/* Payments */}
        {features.payments && (
          <>
            <Route path="/app/billing" element={<Billing />} />
            <Route path="/app/checkout" element={<Checkout />} />
            <Route path="/app/checkout/success" element={<CheckoutSuccess />} />
            <Route path="/app/checkout/cancel" element={<CheckoutCancel />} />
          </>
        )}

        {/* Marketplace (can be feature-flagged next) */}
        <Route path="/app/marketplace" element={<Marketplace />} />

        {/* -------------------- LEGACY APP ALIASES -------------------- */}
        <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
        <Route path="/agents" element={<Navigate to="/app/agents" replace />} />
        <Route path="/settings" element={<Navigate to="/app/settings" replace />} />
        <Route path="/billing" element={<Navigate to="/app/billing" replace />} />
        <Route path="/checkout" element={<Navigate to="/app/checkout" replace />} />
        <Route path="/chat" element={<Navigate to="/app/chat" replace />} />
        <Route path="/chat/:threadId" element={<ChatThreadRedirect />} />
        <Route path="/marketplace" element={<Navigate to="/app/marketplace" replace />} />
        <Route path="/welcome" element={<Navigate to="/demo" replace />} />

        {/* Legacy onboarding aliases */}
        <Route path="/onboarding/guide" element={<Navigate to="/app/onboarding" replace />} />
        <Route path="/onboarding/checklist" element={<Navigate to="/app/onboarding/checklist" replace />} />
        <Route path="/onboarding/profile" element={<Navigate to="/app/onboarding/profile" replace />} />
        <Route path="/onboarding/customer" element={<Navigate to="/app/onboarding/customer" replace />} />
        <Route path="/onboarding/developer" element={<Navigate to="/app/onboarding/developer" replace />} />

        {/* -------------------- MISC / TEST -------------------- */}
        <Route path="/test/logo" element={<LogoTestPage />} />

        {/* Default fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
