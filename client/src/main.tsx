import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

// ChatKit provider (becomes a no-op when disabled per your updated provider file)
import { ChatKitProvider } from "./components/chat/ChatKitProvider";
import ChatLauncher from "./components/chat/ChatLauncher";
import { AuthProvider } from "./features/auth/AuthContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

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
