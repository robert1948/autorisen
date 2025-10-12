import { ReactNode } from "react";

import { useAuth } from "./AuthContext";

const AuthGate = ({ children, fallback }: { children: ReactNode; fallback?: ReactNode }) => {
  const { state } = useAuth();
  if (!state.accessToken) {
    return fallback ?? <p className="auth-gate-message">Please log in to access this section.</p>;
  }
  return <>{children}</>;
};

export default AuthGate;
