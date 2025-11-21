import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

// ChatKit provider (becomes a no-op when disabled per your updated provider file)
import { ChatKitProvider } from "./components/chat/ChatKitProvider";
import ChatLauncher from "./components/chat/ChatLauncher";
import { AuthProvider } from "./features/auth/AuthContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { loadConfig } from "./config";
import { registerServiceWorker } from "./serviceWorker";

// Feature flag (set on Heroku: VITE_ENABLE_CHATKIT=false to park chat)
const CHATKIT_ENABLED = import.meta.env.VITE_ENABLE_CHATKIT === "true";

const queryClient = new QueryClient();

const RootApp = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <App />
      {CHATKIT_ENABLED && <ChatLauncher />}
    </AuthProvider>
  </QueryClientProvider>
);

const rootEl = document.getElementById("root");
if (!rootEl) {
  throw new Error("Root element #root not found");
}

// Load runtime config before mounting the app
loadConfig()
  .then((config) => {
    // Make config available globally for existing API code
    window.__CC_CONFIG__ = config;
    console.log("🚀 AutoLocal/CapeControl loaded", {
      version: config.VERSION,
      environment: config.ENVIRONMENT,
      apiBase: config.API_BASE_URL
    });

    // Register service worker for production caching
    registerServiceWorker();

    // Mount the React app
    ReactDOM.createRoot(rootEl).render(
      <React.StrictMode>
        {CHATKIT_ENABLED ? (
          <ChatKitProvider>
            <RootApp />
          </ChatKitProvider>
        ) : (
          <RootApp />
        )}
      </React.StrictMode>
    );
  })
  .catch((error) => {
    console.error("Failed to load app config:", error);
    
    // Fallback: still mount the app with default config
    ReactDOM.createRoot(rootEl).render(
      <React.StrictMode>
        {CHATKIT_ENABLED ? (
          <ChatKitProvider>
            <RootApp />
          </ChatKitProvider>
        ) : (
          <RootApp />
        )}
      </React.StrictMode>
    );
  });
