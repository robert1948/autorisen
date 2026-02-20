/**
 * AppShell — shared layout wrapper for all authenticated /app/* pages.
 *
 * Provides:
 *   - Collapsible sidebar navigation (desktop/tablet)
 *   - Bottom navigation bar (mobile)
 *   - Top header with breadcrumb + user menu
 *   - Responsive: sidebar expanded (lg+), collapsed icons (md), hidden + bottom nav (sm)
 */

import { useState, useCallback } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";
import { useProfile } from "../../hooks/useProfile";
import { features } from "../../config/features";
import { hasPermission } from "../../utils/permissions";

/* ── SVG icon components ─────────────────────────────── */

function DashboardIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1" />
    </svg>
  );
}

function ProjectsIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
    </svg>
  );
}

function AgentsIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  );
}

function ChatIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  );
}

function MarketplaceIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
    </svg>
  );
}

function BillingIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
    </svg>
  );
}

function SettingsIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}

function LogoutIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
  );
}

function MenuIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
}

function CloseIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function ComplianceIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  );
}

/* ── Navigation items ──────────────────────────────── */

interface NavItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  permission?: string;
  featureFlag?: boolean;
  mobile?: boolean; // shown in bottom nav
}

function useNavItems(): NavItem[] {
  const { user } = useProfile();

  const items: NavItem[] = [
    { to: "/app/dashboard", label: "Dashboard", icon: DashboardIcon, mobile: true },
    { to: "/app/projects/new", label: "Projects", icon: ProjectsIcon, mobile: true },
  ];

  if (features.agentsShell) {
    items.push(
      { to: "/app/agents", label: "Agents", icon: AgentsIcon, mobile: true },
      { to: "/app/chat", label: "Chat", icon: ChatIcon, mobile: false },
    );
  }

  items.push({ to: "/app/marketplace", label: "Marketplace", icon: MarketplaceIcon, mobile: false });
  items.push({ to: "/app/compliance", label: "Compliance", icon: ComplianceIcon, mobile: false });

  if (features.payments) {
    items.push(
      { to: "/app/pricing", label: "Pricing", icon: MarketplaceIcon, mobile: false },
      { to: "/app/billing", label: "Billing", icon: BillingIcon, mobile: false },
    );
  }

  items.push({ to: "/app/settings", label: "Settings", icon: SettingsIcon, mobile: true });

  // Filter by permissions
  return items.filter((item) => {
    if (item.permission && user && !hasPermission(user, item.permission)) return false;
    if (item.featureFlag === false) return false;
    return true;
  });
}

/* ── Sidebar link ──────────────────────────────────── */

function SidebarLink({ item, collapsed }: { item: NavItem; collapsed: boolean }) {
  return (
    <NavLink
      to={item.to}
      end={item.to === "/app/dashboard"}
      className={({ isActive }) =>
        `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150 ${
          isActive
            ? "bg-blue-600/10 text-blue-600 dark:bg-blue-500/15 dark:text-blue-400"
            : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
        } ${collapsed ? "justify-center px-2" : ""}`
      }
      title={collapsed ? item.label : undefined}
    >
      <item.icon className="w-5 h-5 flex-shrink-0" />
      {!collapsed && <span className="truncate">{item.label}</span>}
    </NavLink>
  );
}

/* ── Main AppShell ─────────────────────────────────── */

export function AppShell() {
  const { logout } = useAuth();
  const { user } = useProfile();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const navItems = useNavItems();

  const handleLogout = useCallback(async () => {
    await logout();
    navigate("/auth/login");
  }, [logout, navigate]);

  const greeting = user?.displayName || user?.name || user?.email?.split("@")[0] || "User";
  const initials = greeting.slice(0, 2).toUpperCase();

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
      {/* ── Mobile sidebar overlay ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ── Sidebar ── */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 flex flex-col border-r border-slate-200 bg-white
          transition-all duration-300 ease-in-out dark:border-slate-800 dark:bg-slate-900
          lg:static lg:z-auto
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          ${collapsed ? "w-[72px]" : "w-64"}
        `}
      >
        {/* Logo area */}
        <div className={`flex h-16 items-center border-b border-slate-200 dark:border-slate-800 ${collapsed ? "justify-center px-2" : "justify-between px-4"}`}>
          {!collapsed && (
            <Link to="/app/dashboard" className="flex items-center gap-2">
              <img src="/icons/logo-64x64.png" alt="CapeControl" className="h-8 w-8 rounded-lg" />
              <span className="text-lg font-bold text-slate-900 dark:text-white">CapeControl</span>
            </Link>
          )}
          {collapsed && (
            <Link to="/app/dashboard">
              <img src="/icons/logo-64x64.png" alt="CapeControl" className="h-8 w-8 rounded-lg" />
            </Link>
          )}
          {/* Close button (mobile) */}
          <button
            onClick={() => setSidebarOpen(false)}
            className="rounded-md p-1 text-slate-400 hover:text-slate-600 lg:hidden"
            aria-label="Close sidebar"
          >
            <CloseIcon />
          </button>
          {/* Collapse toggle (desktop) */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className={`hidden rounded-md p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 lg:block ${collapsed ? "absolute -right-3 top-5 z-10 rounded-full border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800" : ""}`}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d={collapsed ? "M9 5l7 7-7 7" : "M15 19l-7-7 7-7"} />
            </svg>
          </button>
        </div>

        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <div className="space-y-1">
            {navItems.map((item) => (
              <SidebarLink key={item.to} item={item} collapsed={collapsed} />
            ))}
          </div>
        </nav>

        {/* User section at bottom */}
        <div className={`border-t border-slate-200 p-3 dark:border-slate-800 ${collapsed ? "flex flex-col items-center gap-2" : ""}`}>
          {!collapsed ? (
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-sm font-bold text-white">
                {initials}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-200">{greeting}</p>
                <p className="truncate text-xs text-slate-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="rounded-md p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                title="Sign out"
                aria-label="Sign out"
              >
                <LogoutIcon className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <>
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-xs font-bold text-white" title={greeting}>
                {initials}
              </div>
              <button
                onClick={handleLogout}
                className="rounded-md p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600"
                title="Sign out"
                aria-label="Sign out"
              >
                <LogoutIcon className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      </aside>

      {/* ── Main content area ── */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top header bar */}
        <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-slate-900 lg:px-6">
          {/* Mobile menu button */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="rounded-md p-1.5 text-slate-500 hover:text-slate-700 lg:hidden"
            aria-label="Open sidebar"
          >
            <MenuIcon />
          </button>

          {/* Spacer for desktop (sidebar handles logo) */}
          <div className="hidden lg:block" />

          {/* Right side actions */}
          <div className="flex items-center gap-3">
            {/* System status dot */}
            <span className="flex h-2.5 w-2.5 rounded-full bg-green-500" title="All systems operational" />
            <Link
              to="/app/settings"
              className="rounded-md p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              aria-label="Settings"
            >
              <SettingsIcon className="h-5 w-5" />
            </Link>
          </div>
        </header>

        {/* Content area with scroll */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>

        {/* ── Mobile bottom navigation ── */}
        <nav className="flex border-t border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 lg:hidden"
          role="navigation"
          aria-label="Mobile navigation"
        >
          {navItems.filter(i => i.mobile).map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/app/dashboard"}
              className={({ isActive }) =>
                `flex flex-1 flex-col items-center gap-0.5 py-2.5 text-[10px] font-medium transition-colors ${
                  isActive
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                }`
              }
            >
              <item.icon className="h-5 w-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}

export default AppShell;
