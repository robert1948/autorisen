import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import App from "./App";
import "./index.css";
import { ChatKitProvider } from "./components/chat/ChatKitProvider";
import { AuthProvider } from "./features/auth/AuthContext";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ChatKitProvider>
          <App />
        </ChatKitProvider>
      </AuthProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
