```mermaid
flowchart TD
    %% Public Pages
    A[🏠 Landing Page '/'] --> B{User Action}
    B -->|Sign Up| C[📝 Register '/register']
    B -->|Sign In| D[🔑 Login '/login']
    B -->|Learn More| E[ℹ️ About '/about']
    B -->|View Pricing| F[💰 Subscribe '/subscribe']
    
    %% Authentication Flow
    C --> G[📧 Email Verification]
    G -->|Success| H[🎉 Welcome '/welcome']
    D --> I{Auth Success?}
    I -->|Yes| J{First Time?}
    I -->|No| K[❌ Login Error]
    K --> D
    
    %% Onboarding Flow
    H --> L[🧭 Onboarding Guide '/onboarding/guide']
    J -->|First Login| L
    J -->|Returning User| M[📊 Dashboard '/dashboard']
    
    L --> N{Choose Path}
    N -->|Customer| O[👤 Customer Onboarding '/onboarding/customer']
    N -->|Developer| P[⚡ Developer Onboarding '/onboarding/developer']
    N -->|Skip| Q[📋 Profile Setup '/onboarding/profile']
    
    O --> Q
    P --> Q
    Q --> R[✅ Onboarding Checklist '/onboarding/checklist']
    
    %% Checklist Items
    R --> S{Required Items Complete?}
    S -->|No| T[Complete Profile]
    S -->|No| U[Verify Email]
    S -->|No| V[Watch Guide]
    T --> Q
    U --> G
    V --> L
    S -->|Yes| M
    
    %% Dashboard & App Features
    M --> W[⚙️ Settings]
    M --> X[🤖 Agents]
    M --> Y[🛒 Marketplace]
    M --> Z[👤 Profile]
    
    %% Password Reset Flow
    D --> AA[🔄 Forgot Password '/forgot-password']
    AA --> AB[📧 Reset Email Sent]
    AB --> AC[🔑 Reset Password '/reset-password']
    AC --> D
    
    %% Social Auth
    D --> AD[🔗 Social Login]
    AD --> AE[🔄 OAuth Callback '/auth/callback']
    AE --> I
    
    %% MFA Flow
    I -->|MFA Required| AF[🔐 MFA Challenge '/auth/mfa']
    AF -->|Success| J
    AF -->|Setup Required| AG[📱 MFA Enroll '/account/mfa-enroll']
    AG --> AF
    
    %% Styling
    classDef public fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef auth fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef onboarding fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef dashboard fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef decision fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef security fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    
    class A,E,F public
    class C,D,G,H,K,AA,AB,AC,AD,AE auth
    class L,N,O,P,Q,R,T,U,V onboarding
    class M,W,X,Y,Z dashboard
    class B,I,J,S decision
    class AF,AG security
```text
## CapeControl User Flow Architecture

### 🎯 Flow Summary

**Public Access** → **Authentication** → **Onboarding** → **Main Application**

### 📱 Key User Paths

1. **New User Journey**:

   ```text
   Landing → Register → Email Verify → Welcome → Onboarding Guide → Profile → Checklist → Dashboard
   ```

1. **Returning User**:

   ```text
   Landing → Login → Dashboard
   ```

1. **Password Recovery**:

   ```text
   Login → Forgot Password → Reset Email → Reset Password → Login
   ```

1. **Social Authentication**:

   ```text
   Login → Social Login → OAuth Callback → Dashboard
   ```

### 🔐 Security Features

- **Multi-Factor Authentication (MFA)** with enrollment flow
- **Email verification** required for account activation
- **Password reset** with secure token validation
- **OAuth integration** for Google/LinkedIn
- **CSRF protection** throughout authentication flow

### 🧭 Onboarding Strategy

- **Guided experience** with step-by-step progression
- **Role-based paths** (Customer vs Developer)
- **Progress tracking** with completion checklist
- **Required vs optional** onboarding items
- **Skip options** for experienced users

### 📊 Dashboard Features

- **Activity monitoring** with real-time updates
- **Agent management** and deployment
- **Marketplace access** for discovering new tools
- **User profile** and settings management
- **Quick actions** for common tasks

### 🎨 Page Categories

- 🔵 **Public Pages**: Accessible without authentication
- 🟣 **Authentication**: Login, registration, and security
- 🟢 **Onboarding**: First-time user experience
- 🟠 **Dashboard**: Main application features
- 🔴 **Security**: MFA and advanced authentication
- 🟡 **Decision Points**: User choice interactions
