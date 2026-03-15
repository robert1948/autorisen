import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "./features/auth/AuthContext";

import { loadConfig } from "./config";
import { registerServiceWorker } from "./serviceWorker";

// Feature flag (set on Heroku: VITE_ENABLE_CHATKIT=false to park chat)
const CHATKIT_ENABLED = import.meta.env.VITE_ENABLE_CHATKIT === "true";

// ChatKit (lazy-loaded only when enabled to reduce critical bundle size)
const ChatKitProvider = CHATKIT_ENABLED
  ? React.lazy(() => import("./components/chat/ChatKitProvider").then(m => ({ default: m.ChatKitProvider })))
  : ({ children }: { children: React.ReactNode }) => <>{children}</>;
const ChatLauncher = CHATKIT_ENABLED
  ? React.lazy(() => import("./components/chat/ChatLauncher"))
  : () => null;

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
      <React.Suspense fallback={null}>
        {CHATKIT_ENABLED ? (
          <ChatKitProvider>
            <RootApp />
          </ChatKitProvider>
        ) : (
          <RootApp />
        )}
      </React.Suspense>
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
