import React from "react";
import MvpScaffoldPage from "./MvpScaffoldPage";

export const MvpLanding = () => (
  <MvpScaffoldPage
    title="Landing"
    route="/"
    access="public"
    data="none"
    links={[
      { to: "/login", label: "Login" },
      { to: "/register", label: "Register" },
    ]}
  />
);

export const MvpAbout = () => (
  <MvpScaffoldPage title="About" route="/about" access="public" data="none" />
);

export const MvpDocs = () => (
  <MvpScaffoldPage title="Docs" route="/docs" access="public" data="none" />
);

export const MvpLogin = () => (
  <MvpScaffoldPage
    title="Login"
    route="/login"
    access="public"
    data="write"
    links={[{ to: "/", label: "Back to Landing" }, { to: "/register", label: "Register" }]}
  />
);

export const MvpRegister = () => (
  <MvpScaffoldPage
    title="Register"
    route="/register"
    access="public"
    data="write"
    links={[{ to: "/", label: "Back to Landing" }, { to: "/login", label: "Login" }]}
  />
);

export const MvpResetPassword = () => (
  <MvpScaffoldPage
    title="Reset Password"
    route="/reset-password"
    access="public"
    data="write"
    links={[{ to: "/login", label: "Back to Login" }, { to: "/", label: "Landing" }]}
  />
);

export const MvpResetPasswordConfirm = () => (
  <MvpScaffoldPage
    title="Reset Password Confirm"
    route="/reset-password/confirm"
    access="public"
    data="write"
    links={[{ to: "/login", label: "Back to Login" }]}
  />
);

export const MvpRegisterStep1 = () => (
  <MvpScaffoldPage
    title="Register — Step 1"
    route="/register/step-1"
    access="public"
    data="write"
    links={[{ to: "/register", label: "Back to Register" }]}
  />
);

export const MvpRegisterStep2 = () => (
  <MvpScaffoldPage
    title="Register — Step 2"
    route="/register/step-2"
    access="public"
    data="write"
    links={[{ to: "/register/step-1", label: "Back to Step 1" }]}
  />
);

export const MvpVerifyEmail = () => (
  <MvpScaffoldPage
    title="Verify Email"
    route="/verify-email/:token"
    access="public"
    data="write"
    links={[{ to: "/login", label: "Back to Login" }]}
  />
);

export const MvpLogout = () => (
  <MvpScaffoldPage
    title="Logout"
    route="/logout"
    access="auth"
    data="write"
    links={[{ to: "/login", label: "Go to Login" }]}
  />
);

export const MvpOnboardingWelcome = () => (
  <MvpScaffoldPage
    title="Onboarding — Welcome"
    route="/onboarding/welcome"
    access="onboarding"
    data="write"
  />
);

export const MvpOnboardingProfile = () => (
  <MvpScaffoldPage
    title="Onboarding — Profile"
    route="/onboarding/profile"
    access="onboarding"
    data="write"
  />
);

export const MvpOnboardingChecklist = () => (
  <MvpScaffoldPage
    title="Onboarding — Checklist"
    route="/onboarding/checklist"
    access="onboarding"
    data="write"
  />
);

export const MvpOnboardingGuide = () => (
  <MvpScaffoldPage
    title="Onboarding — Guide"
    route="/onboarding/guide"
    access="onboarding"
    data="read-only"
  />
);

export const MvpDashboard = () => (
  <MvpScaffoldPage
    title="Dashboard"
    route="/dashboard"
    access="app"
    data="read-only"
    links={[
      { to: "/settings", label: "Settings" },
      { to: "/help", label: "Help" },
    ]}
  />
);

export const MvpSettings = () => (
  <MvpScaffoldPage title="Settings" route="/settings" access="app" data="read-only" />
);

export const MvpSettingsProfile = () => (
  <MvpScaffoldPage
    title="Settings — Profile"
    route="/settings/profile"
    access="app"
    data="write"
  />
);

export const MvpSettingsSecurity = () => (
  <MvpScaffoldPage
    title="Settings — Security"
    route="/settings/security"
    access="app"
    data="write"
  />
);

export const MvpSettingsBilling = () => (
  <MvpScaffoldPage
    title="Settings — Billing"
    route="/settings/billing"
    access="app"
    data="read-only"
  />
);

export const MvpHelp = () => (
  <MvpScaffoldPage title="Help" route="/help" access="help" data="read-only" />
);

export const MvpKnowledgeBase = () => (
  <MvpScaffoldPage
    title="Knowledge Base"
    route="/help/knowledge-base"
    access="help"
    data="read-only"
  />
);
