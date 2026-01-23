<?xml version="1.0" encoding="UTF-8"?>
<map version="1.0.1">
  <node CREATED="1699459200" ID="root" MODIFIED="1699459200" TEXT="🏠 CapeControl User Flow">
    <font BOLD="true" NAME="SansSerif" SIZE="14"/>
    <node CREATED="1699459200" ID="public" MODIFIED="1699459200" POSITION="right" TEXT="🔵 Public Access">
      <edge COLOR="#0277bd" STYLE="sharp_bezier" WIDTH="2"/>
      <font NAME="SansSerif" SIZE="12"/>
      <node CREATED="1699459200" ID="landing" MODIFIED="1699459200" TEXT="🏠 Landing Page '/'">
        <font NAME="SansSerif" SIZE="10"/>
      </node>
      <node CREATED="1699459200" ID="about" MODIFIED="1699459200" TEXT="ℹ️ About '/about'">
        <font NAME="SansSerif" SIZE="10"/>
      </node>
      <node CREATED="1699459200" ID="subscribe" MODIFIED="1699459200" TEXT="💰 Subscribe '/subscribe'">
        <font NAME="SansSerif" SIZE="10"/>
      </node>
    </node>
    <node CREATED="1699459200" ID="auth" MODIFIED="1699459200" POSITION="right" TEXT="🟣 Authentication">
      <edge COLOR="#7b1fa2" STYLE="sharp_bezier" WIDTH="2"/>
      <font NAME="SansSerif" SIZE="12"/>
      <node CREATED="1699459200" ID="register" MODIFIED="1699459200" TEXT="📝 Register '/register'">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="email-verify" MODIFIED="1699459200" TEXT="📧 Email Verification">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="welcome" MODIFIED="1699459200" TEXT="🎉 Welcome '/welcome'">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
      </node>
      <node CREATED="1699459200" ID="login" MODIFIED="1699459200" TEXT="🔑 Login '/login'">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="mfa-challenge" MODIFIED="1699459200" TEXT="🔐 MFA Challenge '/auth/mfa'">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="mfa-enroll" MODIFIED="1699459200" TEXT="📱 MFA Enroll '/account/mfa-enroll'">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
      </node>
      <node CREATED="1699459200" ID="password-reset" MODIFIED="1699459200" TEXT="🔄 Password Reset">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="forgot-password" MODIFIED="1699459200" TEXT="🔄 Forgot Password '/forgot-password'">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="reset-password" MODIFIED="1699459200" TEXT="🔑 Reset Password '/reset-password'">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
      </node>
      <node CREATED="1699459200" ID="social-auth" MODIFIED="1699459200" TEXT="🔗 Social Authentication">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="oauth-callback" MODIFIED="1699459200" TEXT="🔄 OAuth Callback '/auth/callback'">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
      </node>
    </node>
    <node CREATED="1699459200" ID="onboarding" MODIFIED="1699459200" POSITION="left" TEXT="🟢 Onboarding Flow">
      <edge COLOR="#388e3c" STYLE="sharp_bezier" WIDTH="2"/>
      <font NAME="SansSerif" SIZE="12"/>
      <node CREATED="1699459200" ID="guide" MODIFIED="1699459200" TEXT="🧭 Onboarding Guide '/onboarding/guide'">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="customer-path" MODIFIED="1699459200" TEXT="👤 Customer Path '/onboarding/customer'">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="developer-path" MODIFIED="1699459200" TEXT="⚡ Developer Path '/onboarding/developer'">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
      </node>
      <node CREATED="1699459200" ID="profile" MODIFIED="1699459200" TEXT="📋 Profile Setup '/onboarding/profile'">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="basic-info" MODIFIED="1699459200" TEXT="Basic Information">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="experience" MODIFIED="1699459200" TEXT="Experience Level">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="interests" MODIFIED="1699459200" TEXT="Areas of Interest">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="notifications" MODIFIED="1699459200" TEXT="Notification Preferences">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
      </node>
      <node CREATED="1699459200" ID="checklist" MODIFIED="1699459200" TEXT="✅ Onboarding Checklist '/onboarding/checklist'">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="required" MODIFIED="1699459200" TEXT="Required Items">
          <font NAME="SansSerif" SIZE="9"/>
          <node CREATED="1699459200" ID="complete-profile" MODIFIED="1699459200" TEXT="Complete Profile">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="verify-email" MODIFIED="1699459200" TEXT="Verify Email">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
        </node>
        <node CREATED="1699459200" ID="optional" MODIFIED="1699459200" TEXT="Optional Items">
          <font NAME="SansSerif" SIZE="9"/>
          <node CREATED="1699459200" ID="watch-guide" MODIFIED="1699459200" TEXT="Watch Welcome Guide">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="first-agent" MODIFIED="1699459200" TEXT="Try First Agent">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="explore-marketplace" MODIFIED="1699459200" TEXT="Explore Marketplace">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="setup-notifications" MODIFIED="1699459200" TEXT="Set Up Notifications">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
        </node>
      </node>
    </node>
    <node CREATED="1699459200" ID="dashboard" MODIFIED="1699459200" POSITION="left" TEXT="🟠 Main Application">
      <edge COLOR="#f57c00" STYLE="sharp_bezier" WIDTH="2"/>
      <font NAME="SansSerif" SIZE="12"/>
      <node CREATED="1699459200" ID="access-control" MODIFIED="1699459200" TEXT="🔒 Access Control (RequireAuth)">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="access-control-unauthenticated" MODIFIED="1699459200" TEXT="Unauthenticated → SoftGateInterstitial (Login + Create free account)">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="access-control-authenticated" MODIFIED="1699459200" TEXT="Authenticated → Outlet (protected pages)">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
      </node>

      <node CREATED="1699459200" ID="agent-interaction-flow" MODIFIED="1699459200" TEXT="🧩 Agent Interaction Flow">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="agent-discover" MODIFIED="1699459200" TEXT="Discover Agent">
          <font NAME="SansSerif" SIZE="9"/>
          <node CREATED="1699459200" ID="agent-discover-marketplace" MODIFIED="1699459200" TEXT="Marketplace / Browse">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="agent-discover-recommendations" MODIFIED="1699459200" TEXT="Recommendations (CapeAI)">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="agent-discover-trust" MODIFIED="1699459200" TEXT="Trust Signals (ratings, verified publisher, usage)">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
        </node>
        <node CREATED="1699459200" ID="agent-detail" MODIFIED="1699459200" TEXT="Agent Detail View">
          <font NAME="SansSerif" SIZE="9"/>
          <node CREATED="1699459200" ID="agent-detail-manifest" MODIFIED="1699459200" TEXT="Public Manifest (redacted)">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="agent-detail-capabilities" MODIFIED="1699459200" TEXT="Capabilities &amp; Limits">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="agent-detail-permissions" MODIFIED="1699459200" TEXT="Permissions Requested">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
        </node>
        <node CREATED="1699459200" ID="agent-use" MODIFIED="1699459200" TEXT="Use Agent">
          <font NAME="SansSerif" SIZE="9"/>
          <node CREATED="1699459200" ID="agent-use-soft-gate" MODIFIED="1699459200" TEXT="Soft Gate if unauthenticated">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="agent-use-permission-prompt" MODIFIED="1699459200" TEXT="Permission Prompt (first use)">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="agent-use-runtime" MODIFIED="1699459200" TEXT="Execution via Agent Runtime">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
        </node>
        <node CREATED="1699459200" ID="agent-feedback" MODIFIED="1699459200" TEXT="Post-Use Feedback">
          <font NAME="SansSerif" SIZE="9"/>
          <node CREATED="1699459200" ID="agent-feedback-summary" MODIFIED="1699459200" TEXT="Result Summary">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="agent-feedback-review" MODIFIED="1699459200" TEXT="Rate / Review">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="agent-feedback-save" MODIFIED="1699459200" TEXT="Save / Reuse / Automate">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
        </node>
      </node>

      <node CREATED="1699459200" ID="dashboard-main" MODIFIED="1699459200" TEXT="📊 Dashboard '/app/dashboard' (legacy: /dashboard)">
        <font NAME="SansSerif" SIZE="10"/>
        <node CREATED="1699459200" ID="stats" MODIFIED="1699459200" TEXT="📈 Stats Overview">
          <font NAME="SansSerif" SIZE="9"/>
          <node CREATED="1699459200" ID="active-agents" MODIFIED="1699459200" TEXT="Active Agents">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="tasks-complete" MODIFIED="1699459200" TEXT="Tasks Complete">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="system-status" MODIFIED="1699459200" TEXT="System Status">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
        </node>
        <node CREATED="1699459200" ID="activity" MODIFIED="1699459200" TEXT="🔄 Recent Activity">
          <font NAME="SansSerif" SIZE="9"/>
        </node>
        <node CREATED="1699459200" ID="quick-actions" MODIFIED="1699459200" TEXT="⚡ Quick Actions">
          <font NAME="SansSerif" SIZE="9"/>
          <node CREATED="1699459200" ID="deploy-agent" MODIFIED="1699459200" TEXT="Deploy New Agent">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="browse-marketplace" MODIFIED="1699459200" TEXT="Browse Marketplace">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
          <node CREATED="1699459200" ID="system-settings" MODIFIED="1699459200" TEXT="System Settings">
            <font NAME="SansSerif" SIZE="8"/>
          </node>
        </node>
      </node>
      <node CREATED="1699459200" ID="agents" MODIFIED="1699459200" TEXT="🤖 Agents Management '/app/agents' (legacy: /agents)">
        <font NAME="SansSerif" SIZE="10"/>
      </node>
      <node CREATED="1699459200" ID="marketplace" MODIFIED="1699459200" TEXT="🛒 Marketplace">
        <font NAME="SansSerif" SIZE="10"/>
      </node>
      <node CREATED="1699459200" ID="user-profile" MODIFIED="1699459200" TEXT="👤 User Profile">
        <font NAME="SansSerif" SIZE="10"/>
      </node>
      <node CREATED="1699459200" ID="settings" MODIFIED="1699459200" TEXT="⚙️ Settings '/app/settings' (legacy: /settings)">
        <font NAME="SansSerif" SIZE="10"/>
      </node>
    </node>
  </node>
</map>