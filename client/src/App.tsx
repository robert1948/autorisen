import React from "react";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";

import { features } from "./config/features";

// MVP scaffold routes (Spec-driven)
import RequireMvpAuth from "./routes/guards/RequireMvpAuth";
import RequireMvpGuest from "./routes/guards/RequireMvpGuest";
import RequireAuth from "./routes/guards/RequireAuth";
import {
  MvpLanding,
  MvpAbout,
  MvpDocs,
  MvpLogin,
  MvpRegister,
  MvpResetPassword,
  MvpResetPasswordConfirm,
  MvpRegisterStep1,
  MvpRegisterStep2,
  MvpVerifyEmail,
  MvpLogout,
  MvpOnboardingWelcome,
  MvpOnboardingProfile,
  MvpOnboardingChecklist,
  MvpOnboardingGuide,
  MvpDashboard,
  MvpSettings,
  MvpSettingsProfile,
  MvpSettingsSecurity,
  MvpSettingsBilling,
  MvpHelp,
  MvpKnowledgeBase,
} from "./pages/mvp/MvpPages";

// Public
import HomePage from "./pages/public/HomePage";
import Welcome from "./pages/public/WelcomePage";
import About from "./pages/public/AboutPage";
import Subscribe from "./pages/public/SubscribePage";
import PrivacyPage from "./pages/public/PrivacyPage";
import TermsPage from "./pages/public/TermsPage";
import ContactPage from "./pages/public/ContactPage";
import DeveloperHubPage from "./pages/public/DeveloperHubPage";
import ApiDocsPage from "./pages/public/ApiDocsPage";

// Landing
import LandingPage from "./pages/Landing";
import ExplorePage from "./pages/ExplorePage";

// Docs
import DocsHomePage from "./pages/docs/DocsHomePage";
import DocReaderPage from "./pages/docs/DocReaderPage";

// Auth pages / flows
import Register from "./pages/auth/RegisterPage";
import ForgotPassword from "./pages/auth/ForgotPasswordPage";
import ResetPassword from "./pages/auth/ResetPasswordPage";
import SocialCallback from "./pages/auth/SocialCallbackPage";
import VerifyEmail from "./pages/public/VerifyEmailPage";
import VerifyEmailPendingPage from "./pages/auth/VerifyEmailPendingPage";

// Onboarding pages
import OnboardingCustomer from "./pages/onboarding/OnboardingCustomerPage";
import OnboardingDeveloper from "./pages/onboarding/OnboardingDeveloperPage";
import OnboardingGuide from "./pages/onboarding/OnboardingGuidePage";
import OnboardingChecklist from "./pages/onboarding/OnboardingChecklistPage";
import OnboardingProfile from "./pages/onboarding/OnboardingProfilePage";

// App pages
import Dashboard from "./pages/app/DashboardPage";
import Marketplace from "./pages/app/MarketplacePage";
import Agents from "./pages/app/AgentsPage";
import Developer from "./pages/app/DeveloperPage";
import Settings from "./pages/app/SettingsPage";
import Billing from "./pages/app/BillingPage";
import Checkout from "./pages/app/CheckoutPage";
import CheckoutSuccess from "./pages/app/CheckoutSuccessPage";
import CheckoutCancel from "./pages/app/CheckoutCancelPage";
import ChatConsole from "./pages/app/ChatConsolePage";
import LogoTestPage from "./pages/help/LogoTestPage";
import SunbirdPilotMobile from "./pages/app/SunbirdPilotMobilePage";

// CapeControl auth components (production-ready)
import LoginPage from "./pages/auth/LoginPage";
import MFAChallenge from "./pages/auth/MfaChallengePage";
import MFAEnroll from "./pages/auth/MfaEnrollPage";

// Canonical app entry redirect
import AppEntryRedirect from "./pages/app/AppEntryRedirectPage";

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
        {/* -------------------- MVP SCAFFOLD (SYSTEM_SPEC §2.5) -------------------- */}
        {/* Public pages */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<MvpAbout />} />
        <Route path="/explore" element={<ExplorePage />} />
        <Route path="/docs" element={<DocsHomePage />} />
        <Route path="/docs/:slug" element={<DocReaderPage />} />

        {/* Auth flow pages (guest-only stub) */}
        <Route element={<RequireMvpGuest />}>
          <Route path="/login" element={<MvpLogin />} />
          <Route path="/register" element={<MvpRegister />} />
          <Route path="/register/step-1" element={<MvpRegisterStep1 />} />
          <Route path="/register/step-2" element={<MvpRegisterStep2 />} />
        </Route>

        {/* Onboarding + App pages (require auth stub) */}
        <Route element={<RequireMvpAuth />}>
          {/* Onboarding */}
          <Route path="/onboarding/welcome" element={<MvpOnboardingWelcome />} />
          <Route path="/onboarding/profile" element={<MvpOnboardingProfile />} />
          <Route path="/onboarding/checklist" element={<MvpOnboardingChecklist />} />
          <Route path="/onboarding/guide" element={<MvpOnboardingGuide />} />

          {/* App core */}
          <Route path="/dashboard" element={<MvpDashboard />} />
          <Route path="/settings" element={<MvpSettings />} />
          <Route path="/settings/profile" element={<MvpSettingsProfile />} />
          <Route path="/settings/security" element={<MvpSettingsSecurity />} />
          <Route path="/settings/billing" element={<MvpSettingsBilling />} />

          {/* Logout (action route; placeholder only) */}
          <Route path="/logout" element={<MvpLogout />} />
        </Route>

        {/* Help pages (read-only; public accessible) */}
        <Route path="/help" element={<MvpHelp />} />
        <Route path="/help/knowledge-base" element={<MvpKnowledgeBase />} />

        {/* -------------------- PUBLIC -------------------- */}
        <Route path="/home" element={<HomePage />} />
        <Route path="/demo" element={<Welcome />} />
        <Route path="/how-it-works" element={<About />} />
        <Route path="/subscribe" element={<Subscribe />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/developer-hub" element={<DeveloperHubPage />} />
        <Route path="/api-docs" element={<ApiDocsPage />} />

        {/* -------------------- AUTH (CANONICAL) -------------------- */}
        <Route path="/auth/login" element={<LoginPage />} />
        <Route path="/auth/register" element={<Register />} />
        <Route path="/auth/forgot-password" element={<ForgotPassword />} />
        <Route path="/auth/reset-password" element={<ResetPassword />} />
        <Route path="/auth/verify-email" element={<VerifyEmailPendingPage />} />
        <Route path="/auth/callback" element={<SocialCallback />} />
        <Route path="/auth/verify-email/:token" element={<VerifyEmail />} />

        {/* Legacy email verification links */}
        <Route path="/verify-email/:token" element={<VerifyEmailRedirect />} />

        {/* MFA */}
        <Route
          path="/auth/mfa"
          element={<MFAChallenge onSuccess={() => console.log("MFA Success")} />}
        />
        <Route path="/account/mfa-enroll" element={<MFAEnroll />} />

        {/* -------------------- LEGACY AUTH ALIASES -------------------- */}
        <Route path="/signup" element={<Navigate to="/register" replace />} />
        <Route path="/forgot-password" element={<Navigate to="/auth/forgot-password" replace />} />
        <Route path="/reset-password" element={<Navigate to="/auth/reset-password" replace />} />
        <Route path="/reset-password/confirm" element={<Navigate to="/auth/reset-password" replace />} />

        {/* -------------------- APP (CANONICAL) -------------------- */}
        <Route element={<RequireAuth />}>
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
              <Route path="/app/developer" element={<Developer />} />
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
        </Route>

        {/* -------------------- LEGACY APP ALIASES -------------------- */}
        <Route path="/agents" element={<Navigate to="/app/agents" replace />} />
        <Route path="/developer" element={<Navigate to="/app/developer" replace />} />
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
