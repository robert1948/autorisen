import { Routes, Route } from "react-router-dom";
import { Suspense, lazy } from "react";
import Navbar from "./components/Navbar";
// REMOVE CapeAI System for testing
// import CapeAISystem from "./components/CapeAISystem";

// ✅ Lazy-loaded pages
const Landing = lazy(() => import("./pages/Landing"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/RegisterV2"));

export default function AppTestNoContext() {
  return (
    <div className="min-h-screen flex flex-col font-sans bg-white text-gray-900 dark:bg-gray-900 dark:text-white">
      <Navbar />
      <main className="flex-1 pt-20">
          <Suspense
            fallback={
              <div className="flex items-center justify-center min-h-[50vh]" role="status">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mx-auto"></div>
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading...</p>
                </div>
              </div>
            }
          >
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route
                path="*"
                element={
                  <div className="p-4 text-center text-red-600">
                    404 - Page Not Found
                  </div>
                }
              />
            </Routes>
          </Suspense>
        </main>
        
        {/* CapeAI System - COMMENTED OUT FOR TESTING */}
        {/* <CapeAISystem /> */}
      </div>
  );
}
