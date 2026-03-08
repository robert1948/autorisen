import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./features/auth/AuthContext";

import { loadConfig } from "./config";
import { registerServiceWorker } from "./serviceWorker";

// ChatKit (optional)
import { ChatKitProvider } from "./components/chat/ChatKitProvider";
import ChatLauncher from "./components/chat/ChatLauncher";

// Feature flag (set on Heroku: VITE_ENABLE_CHATKIT=false to park chat)
const CHATKIT_ENABLED = import.meta.env.VITE_ENABLE_CHATKIT === "true";

// Create once (recommended)
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

const mount = () => {
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
};

// Mount immediately for fast FCP, then hydrate config async
mount();

loadConfig()
  .then((config) => {
    window.__CC_CONFIG__ = config;

    console.log("🚀 AutoLocal/CapeControl loaded", {
      version: config.VERSION,
      environment: config.ENVIRONMENT,
      apiBase: config.API_BASE_URL,
      chatkitEnabled: CHATKIT_ENABLED,
    });

    registerServiceWorker();
  })
  .catch((error) => {
    console.error("Failed to load app config:", error);
  });
