import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import useAuth from "./hooks/useAuth";

// Core layout
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

// Feature components
import Subscribe from "./components/Subscribe";
import Credits from "./components/Credits";

// Mini status pill (FE/BE versions)
import StatusBadge from "./components/StatusBadge";

// Lazy pages for faster initial paint
const CustomerDashboard = lazy(() => import("./pages/UserDashboard"));
const DeveloperDashboard = lazy(() => import("./pages/DeveloperDashboard"));
// AdminDashboard not present; reuse DeveloperDashboard for admin routes
const AdminDashboard = lazy(() => import("./pages/DeveloperDashboard"));
const PrivacyPolicy = lazy(() => import("./pages/Privacy"));
const TermsOfService = lazy(() => import("./pages/Terms"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));

/** Simple loading UI for route-level suspense */
function Loader() {
  return (
    <div className="w-full py-10 flex items-center justify-center text-sm text-gray-500">
      Loading…
    </div>
  );
}

/** Protects routes that require authentication; preserves the intended URL */
function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (roles?.length) {
    const userRole = (user?.user_type || user?.role || "").toString();
    const hasRole = roles.some((r) => r.toLowerCase() === userRole.toLowerCase());
    if (!hasRole) return <Navigate to="/" replace />;
  }
  return children;
}

/** Blocks auth pages when the user is already authenticated */
function PublicOnly({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

/** Lightweight 404 page */
function NotFound() {
  return (
    <div className="py-10 text-center text-sm text-gray-500">
      Page not found
    </div>
  );
}

function AppShell() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-6">
        <Suspense fallback={<Loader />}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/login"
              element={
                <PublicOnly>
                  <Login />
                </PublicOnly>
              }
            />
            <Route
              path="/register"
              element={
                <PublicOnly>
                  <Register />
                </PublicOnly>
              }
            />
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="/terms" element={<TermsOfService />} />

            {/* Payments / subscriptions */}
            <Route
              path="/subscribe"
              element={
                <ProtectedRoute>
                  <Subscribe />
                </ProtectedRoute>
              }
            />
            <Route
              path="/credits"
              element={
                <ProtectedRoute>
                  <Credits />
                </ProtectedRoute>
              }
            />

            {/* Dashboards by role */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <CustomerDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dev"
              element={
                <ProtectedRoute roles={["Developer", "Admin"]}>
                  <DeveloperDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute roles={["Admin"]}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />

            {/* Fallback */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
      {/* FE/BE version, commit & env live here */}
      <StatusBadge />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </AuthProvider>
  );
}
