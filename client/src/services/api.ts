/**
 * API service for user profile and onboarding operations
 */

const API_BASE_URL = '/api';

// Types
export interface UserProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company: string;
  role: string;
  experience_level?: string;
  is_email_verified: boolean;
  created_at: string;
  updated_at: string;
  interests: string[];
  notifications_email: boolean;
  notifications_push: boolean;
  notifications_sms: boolean;
}

export interface UserProfileUpdate {
  first_name: string;
  last_name: string;
  company?: string;
  role: string;
  experience_level?: string;
  interests?: string[];
  notifications_email: boolean;
  notifications_push: boolean;
  notifications_sms: boolean;
}

export interface OnboardingChecklistItem {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  required: boolean;
  order: number;
}

export interface OnboardingChecklist {
  items: OnboardingChecklistItem[];
  completion_percentage: number;
  required_completed: number;
  required_total: number;
  optional_completed: number;
  optional_total: number;
}

export interface DashboardStats {
  active_agents: number;
  tasks_complete: number;
  system_status: string;
  agents_deployed: number;
  total_runs: number;
  success_rate: number;
}

export interface ActivityItem {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
  status: string;
  metadata?: Record<string, any>;
}

// API error handling
export class APIError extends Error {
  constructor(public status: number, public message: string) {
    super(message);
    this.name = 'APIError';
  }
}

// Helper function for API calls
async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
    credentials: 'include', // Include cookies for authentication
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new APIError(response.status, errorText || `HTTP ${response.status}`);
  }

  return response.json();
}

// User Profile API
export const userProfileAPI = {
  /**
   * Get current user's profile
   */
  async getProfile(): Promise<UserProfile> {
    return apiCall<UserProfile>('/user/profile');
  },

  /**
   * Update current user's profile
   */
  async updateProfile(profileData: UserProfileUpdate): Promise<UserProfile> {
    return apiCall<UserProfile>('/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },
};

// Onboarding API
export const onboardingAPI = {
  /**
   * Get onboarding checklist for current user
   */
  async getChecklist(): Promise<OnboardingChecklist> {
    return apiCall<OnboardingChecklist>('/user/onboarding/checklist');
  },

  /**
   * Mark an onboarding item as complete
   */
  async completeItem(itemId: string): Promise<{ status: string; item_id: string }> {
    return apiCall<{ status: string; item_id: string }>(
      `/user/onboarding/checklist/item/${itemId}/complete`,
      {
        method: 'POST',
      }
    );
  },
};

// Dashboard API
export const dashboardAPI = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    return apiCall<DashboardStats>('/user/dashboard/stats');
  },

  /**
   * Get recent activity
   */
  async getRecentActivity(limit: number = 10): Promise<ActivityItem[]> {
    return apiCall<ActivityItem[]>(`/user/dashboard/recent-activity?limit=${limit}`);
  },
};

// Combined API export
export const api = {
  userProfile: userProfileAPI,
  onboarding: onboardingAPI,
  dashboard: dashboardAPI,
};