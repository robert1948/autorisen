import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";

import { features } from "./config/features";

// Route guards
import RequireAuth from "./routes/guards/RequireAuth";
import RequireOnboarding from "./routes/guards/RequireOnboarding";

// MVP scaffold pages (content-only stubs — auth/settings routes now redirect to canonical)
import {
  MvpAbout,
  MvpDocs,
  MvpHelp,
  MvpKnowledgeBase,
} from "./pages/mvp/MvpPages";

// Public — HomePage is eagerly loaded (landing page / FCP critical)
import HomePage from "./pages/public/HomePage";
import Home from "./pages/Home";

// Lazy-loaded public pages
const Welcome = lazy(() => import("./pages/public/WelcomePage"));
const About = lazy(() => import("./pages/public/AboutPage"));
const Subscribe = lazy(() => import("./pages/public/SubscribePage"));
const DeveloperInfo = lazy(() => import("./pages/public/DeveloperInfoPage"));
const CustomerInfo = lazy(() => import("./pages/public/CustomerInfoPage"));
const TermsAndConditions = lazy(() => import("./pages/public/TermsAndConditionsPage"));
const DeveloperTerms = lazy(() => import("./pages/public/DeveloperTermsPage"));
const PrivacyPolicy = lazy(() => import("./pages/public/PrivacyPolicyPage"));

// Auth pages / flows (lazy)
const Register = lazy(() => import("./pages/auth/RegisterPage"));
const ForgotPassword = lazy(() => import("./pages/auth/ForgotPasswordPage"));
const ResetPassword = lazy(() => import("./pages/auth/ResetPasswordPage"));
const SocialCallback = lazy(() => import("./pages/auth/SocialCallbackPage"));
const VerifyEmail = lazy(() => import("./pages/public/VerifyEmailPage"));

import { useAuth } from "./features/auth/AuthContext";

// Onboarding pages (lazy)
const OnboardingCustomer = lazy(() => import("./pages/onboarding/OnboardingCustomerPage"));
const OnboardingDeveloper = lazy(() => import("./pages/onboarding/OnboardingDeveloperPage"));
const OnboardingGuide = lazy(() => import("./pages/onboarding/OnboardingGuidePage"));
const OnboardingChecklistPage = lazy(() => import("./pages/onboarding/OnboardingChecklistPage"));
const OnboardingProfilePage = lazy(() => import("./pages/onboarding/OnboardingProfilePage"));
const OnboardingWelcome = lazy(() => import("./pages/onboarding/Welcome"));
const OnboardingProfile = lazy(() => import("./pages/onboarding/Profile"));
const OnboardingChecklist = lazy(() => import("./pages/onboarding/Checklist"));
const OnboardingTrust = lazy(() => import("./pages/onboarding/Trust"));

// App pages (lazy — behind auth gate)
const Dashboard = lazy(() => import("./pages/app/DashboardPage"));
const CreateProjectPage = lazy(() => import("./pages/app/CreateProjectPage"));
const ProjectDetailPage = lazy(() => import("./pages/app/ProjectDetailPage"));
const Marketplace = lazy(() => import("./pages/app/MarketplacePage"));
const Agents = lazy(() => import("./pages/app/AgentsPage"));
const Developer = lazy(() => import("./pages/app/DeveloperPage"));
const Settings = lazy(() => import("./pages/app/SettingsPage"));
const Billing = lazy(() => import("./pages/app/BillingPage"));
const Checkout = lazy(() => import("./pages/app/CheckoutPage"));
const CheckoutSuccess = lazy(() => import("./pages/app/CheckoutSuccessPage"));
const CheckoutCancel = lazy(() => import("./pages/app/CheckoutCancelPage"));
const Pricing = lazy(() => import("./pages/app/PricingPage"));
const ChatConsole = lazy(() => import("./pages/app/ChatConsolePage"));
const CompliancePage = lazy(() => import("./pages/app/CompliancePage"));
const LogoTestPage = lazy(() => import("./pages/help/LogoTestPage"));
const SunbirdPilotMobile = lazy(() => import("./pages/app/SunbirdPilotMobilePage"));

// CapeControl auth components (lazy)
const LoginPage = lazy(() => import("./pages/auth/LoginPage"));
const MFAChallenge = lazy(() => import("./pages/auth/MfaChallengePage"));
const MFAEnroll = lazy(() => import("./pages/auth/MfaEnrollPage"));

// Canonical app entry redirect
import AppEntryRedirect from "./pages/app/AppEntryRedirectPage";

// Shared app shell with sidebar + bottom nav
import { AppShell } from "./components/layout/AppShell";

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

/**
 * Logout route — clears auth state and redirects to login.
 * Calls POST /api/auth/logout via useAuth().logout().
 */
function LogoutAction() {
  const { logout } = useAuth();
  const [done, setDone] = React.useState(false);

  React.useEffect(() => {
    logout().then(() => setDone(true)).catch(() => setDone(true));
  }, [logout]);

  if (done) {
    return <Navigate to="/auth/login" replace />;
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white">
      <p>Signing out…</p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" /></div>}>
      <Routes>
        {/* -------------------- MVP SCAFFOLD (SYSTEM_SPEC §2.5) -------------------- */}
        {/* Public pages */}
        <Route path="/" element={<Home />} />
        <Route path="/landing-legacy" element={<HomePage />} />
        <Route path="/about" element={<MvpAbout />} />
        <Route path="/docs" element={<MvpDocs />} />

        {/* Auth flow aliases — redirect to canonical /auth/* routes */}
        <Route path="/login" element={<Navigate to="/auth/login" replace />} />
        <Route path="/register" element={<Navigate to="/auth/register" replace />} />
        <Route path="/reset-password" element={<Navigate to="/auth/forgot-password" replace />} />
        <Route path="/reset-password/confirm" element={<Navigate to="/auth/reset-password" replace />} />
        <Route path="/register/step-1" element={<Navigate to="/auth/register" replace />} />
        <Route path="/register/step-2" element={<Navigate to="/auth/register" replace />} />

        {/* Email verification — outside auth guards so links always work */}
        <Route path="/verify-email/:token" element={<VerifyEmailRedirect />} />

        {/* Onboarding routes (auth required) */}
        <Route element={<RequireAuth />}>
          <Route path="/onboarding/welcome" element={<OnboardingWelcome />} />
          <Route path="/onboarding/profile" element={<OnboardingProfile />} />
          <Route path="/onboarding/checklist" element={<OnboardingChecklist />} />
          <Route path="/onboarding/trust" element={<OnboardingTrust />} />
        </Route>

        {/* App aliases — redirect to canonical /app/* routes */}
        <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
        <Route path="/settings" element={<Navigate to="/app/settings" replace />} />
        <Route path="/settings/profile" element={<Navigate to="/app/settings" replace />} />
        <Route path="/settings/security" element={<Navigate to="/app/settings" replace />} />
        <Route path="/settings/billing" element={<Navigate to="/app/settings" replace />} />

        {/* Logout — real action: clears tokens and redirects to login */}
        <Route path="/logout" element={<LogoutAction />} />

        {/* Help pages (read-only; public accessible) */}
        <Route path="/help" element={<MvpHelp />} />
        <Route path="/help/knowledge-base" element={<MvpKnowledgeBase />} />

        {/* -------------------- PUBLIC -------------------- */}
        <Route path="/home" element={<HomePage />} />
        <Route path="/demo" element={<Welcome />} />
        <Route path="/how-it-works" element={<About />} />
        <Route path="/subscribe" element={<Subscribe />} />
        <Route path="/developers" element={<DeveloperInfo />} />
        <Route path="/customer-terms" element={<CustomerInfo />} />
        <Route path="/terms-and-conditions" element={<TermsAndConditions />} />
        <Route path="/developer-terms" element={<DeveloperTerms />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />

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
        <Route path="/signup" element={<Navigate to="/auth/register" replace />} />
        <Route path="/forgot-password" element={<Navigate to="/auth/forgot-password" replace />} />

        {/* -------------------- APP (CANONICAL) -------------------- */}
        <Route element={<RequireAuth />}>
          <Route element={<RequireOnboarding />}>
            <Route path="/app" element={<AppEntryRedirect />} />

            {/* Onboarding canonical entry (no AppShell — full-screen flow) */}
            {features.onboarding && (
              <>
                <Route path="/app/onboarding" element={<OnboardingGuide />} />
                <Route
                  path="/app/onboarding/checklist"
                  element={<OnboardingChecklistPage />}
                />
                <Route
                  path="/app/onboarding/profile"
                  element={<OnboardingProfilePage />}
                />
                <Route path="/app/onboarding/customer" element={<OnboardingCustomer />} />
                <Route path="/app/onboarding/developer" element={<OnboardingDeveloper />} />
              </>
            )}

            {/* App pages inside shared shell (sidebar + bottom nav) */}
            <Route element={<AppShell />}>
              <Route path="/app/dashboard" element={<Dashboard />} />
              <Route path="/app/projects/new" element={<CreateProjectPage />} />
              <Route path="/app/projects/:projectId" element={<ProjectDetailPage />} />
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
                  <Route path="/app/pricing" element={<Pricing />} />
                  <Route path="/app/billing" element={<Billing />} />
                  <Route path="/app/checkout" element={<Checkout />} />
                  <Route path="/app/checkout/success" element={<CheckoutSuccess />} />
                  <Route path="/app/checkout/cancel" element={<CheckoutCancel />} />
                </>
              )}

              {/* Marketplace */}
              <Route path="/app/marketplace" element={<Marketplace />} />

              {/* Compliance */}
              <Route path="/app/compliance" element={<CompliancePage />} />
            </Route>
          </Route>
        </Route>

        {/* -------------------- LEGACY APP ALIASES -------------------- */}
        <Route path="/agents" element={<Navigate to="/app/agents" replace />} />
        <Route path="/developer" element={<Navigate to="/app/developer" replace />} />
        <Route path="/billing" element={<Navigate to="/app/billing" replace />} />
        <Route path="/pricing" element={<Navigate to="/app/pricing" replace />} />
        <Route path="/checkout" element={<Navigate to="/app/checkout" replace />} />
        <Route path="/chat" element={<Navigate to="/app/chat" replace />} />
        <Route path="/chat/:threadId" element={<ChatThreadRedirect />} />
        <Route path="/marketplace" element={<Navigate to="/app/marketplace" replace />} />
        <Route path="/welcome" element={<Navigate to="/demo" replace />} />

        {/* Legacy onboarding aliases */}
        <Route path="/onboarding/guide" element={<Navigate to="/onboarding/welcome" replace />} />
        <Route path="/onboarding/customer" element={<Navigate to="/app/onboarding/customer" replace />} />
        <Route path="/onboarding/developer" element={<Navigate to="/app/onboarding/developer" replace />} />

        {/* -------------------- MISC / TEST -------------------- */}
        <Route path="/test/logo" element={<LogoTestPage />} />

        {/* Default fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
