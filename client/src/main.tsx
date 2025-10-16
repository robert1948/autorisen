import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

// ChatKit provider (becomes a no-op when disabled per your updated provider file)
import { ChatKitProvider } from "./components/chat/ChatKitProvider";

// Feature flag (set on Heroku: VITE_ENABLE_CHATKIT=false to park chat)
const CHATKIT_ENABLED = import.meta.env.VITE_ENABLE_CHATKIT === "true";

const rootEl = document.getElementById("root");
if (!rootEl) {
  throw new Error("Root element #root not found");
}

ReactDOM.createRoot(rootEl).render(
  <React.StrictMode>
    {CHATKIT_ENABLED ? (
      <ChatKitProvider>
        <App />
      </ChatKitProvider>
    ) : (
      <App />
    )}
  </React.StrictMode>
);
