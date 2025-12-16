import React from "react";
import { Navigate } from "react-router-dom";

type Props = {
  enabled: boolean;
  children: React.ReactElement;
  redirectTo?: string;
};

export default function FeatureGate({ enabled, children, redirectTo = "/app/dashboard" }: Props) {
  if (!enabled) return <Navigate to={redirectTo} replace />;
  return children;
}
