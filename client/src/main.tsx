import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./index.css";
import { ChatKitProvider } from "./components/chat/ChatKitProvider";
import { AuthProvider } from "./features/auth/AuthContext";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <ChatKitProvider>
        <App />
      </ChatKitProvider>
    </AuthProvider>
  </React.StrictMode>
);
