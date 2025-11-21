export interface AppConfig {
  API_BASE_URL: string;
  VERSION: string;
  ENVIRONMENT: string;
}

let cachedConfig: AppConfig | null = null;

export async function loadConfig(): Promise<AppConfig> {
  if (cachedConfig) {
    return cachedConfig;
  }

  try {
    const response = await fetch("/config.json", { 
      cache: "no-store",
      headers: {
        'Cache-Control': 'no-cache'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.status}`);
    }
    
    cachedConfig = await response.json();
    return cachedConfig!;
  } catch (error) {
    console.warn("Failed to load runtime config, falling back to build-time defaults:", error);
    
    // Fallback to build-time configuration
    cachedConfig = {
      API_BASE_URL: import.meta.env.VITE_API_BASE || "/api",
      VERSION: import.meta.env.VITE_APP_VERSION || "dev",
      ENVIRONMENT: import.meta.env.MODE || "development"
    };
    
    return cachedConfig;
  }
}

// Make config available globally for existing code
declare global {
  interface Window {
    __CC_CONFIG__?: AppConfig;
  }
}

export function getConfig(): AppConfig {
  return window.__CC_CONFIG__ || {
    API_BASE_URL: "/api",
    VERSION: "dev", 
    ENVIRONMENT: "development"
  };
}