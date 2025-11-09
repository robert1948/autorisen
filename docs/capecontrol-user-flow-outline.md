# CapeControl User Flow Architecture

## 🔵 Public Access

- 🏠 Landing Page '/'
- ℹ️ About '/about'
- 💰 Subscribe '/subscribe'

## 🟣 Authentication

### 📝 Register '/register'

- 📧 Email Verification
- 🎉 Welcome '/welcome'

### 🔑 Login '/login'

- 🔐 MFA Challenge '/auth/mfa'
- 📱 MFA Enroll '/account/mfa-enroll'

### 🔄 Password Reset

- 🔄 Forgot Password '/forgot-password'
- 🔑 Reset Password '/reset-password'

### 🔗 Social Authentication

- 🔄 OAuth Callback '/auth/callback'

## 🟢 Onboarding Flow

### 🧭 Onboarding Guide '/onboarding/guide'

- 👤 Customer Path '/onboarding/customer'
- ⚡ Developer Path '/onboarding/developer'

### 📋 Profile Setup '/onboarding/profile'

- Basic Information
  - First Name
  - Last Name
  - Company
  - Role
- Experience Level
  - Beginner
  - Intermediate
  - Advanced
- Areas of Interest
  - Task Automation
  - Data Analysis
  - Content Creation
  - Customer Support
  - Development Tools
  - Marketing
  - Finance
  - HR & Recruiting
- Notification Preferences
  - Email Notifications
  - Push Notifications
  - SMS Notifications

### ✅ Onboarding Checklist '/onboarding/checklist'

#### Required Items

- Complete Profile
- Verify Email

#### Optional Items

- Watch Welcome Guide
- Try First Agent
- Explore Marketplace
- Set Up Notifications

## 🟠 Main Application

### 📊 Dashboard '/dashboard'

#### 📈 Stats Overview

- Active Agents
- Tasks Complete
- System Status

#### 🔄 Recent Activity

- Agent deployments
- System health checks
- User onboarding events

#### ⚡ Quick Actions

- Deploy New Agent
- Browse Marketplace
- System Settings

### 🤖 Agents Management

- Agent listing
- Agent configuration
- Agent deployment
- Agent monitoring

### 🛒 Marketplace

- Browse available agents
- Install agents
- Agent ratings and reviews
- Community contributions

### 👤 User Profile

- Personal information
- Account settings
- Subscription management
- Usage statistics

### ⚙️ Settings

- System preferences
- Security settings
- Notification settings
- Integration settings

## User Journey Flows

### New User Journey

1. Landing Page → Register
1. Email Verification → Welcome
1. Onboarding Guide → Choose Path
1. Profile Setup → Complete Information
1. Onboarding Checklist → Track Progress
1. Dashboard → Start Using Platform

### Returning User Journey

1. Landing Page → Login
1. (Optional MFA Challenge)
1. Dashboard → Continue Work

### Password Recovery

1. Login → Forgot Password
1. Email Reset Link → Reset Password
1. New Password → Login Success

### Social Authentication

1. Login → Social Provider
1. OAuth Authorization → Callback
1. Account Linking → Dashboard
