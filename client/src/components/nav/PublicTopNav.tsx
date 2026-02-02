import { useState } from "react";
import { Link } from "react-router-dom";

import logoUrl from "../../assets/CapeControl_Logo_Transparent.png";

export default function PublicTopNav() {
  const [menuOpen, setMenuOpen] = useState(false);

  const closeMenu = () => setMenuOpen(false);

  return (
    <header className="px-6 py-6">
      <div className="relative">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" onClick={closeMenu}>
            <img
              src={logoUrl}
              alt="CapeControl"
              className="w-9 h-9 rounded-lg bg-white/5 border border-white/10 p-1"
            />
            <span className="text-xl font-bold tracking-tight">CapeControl</span>
          </Link>

          <nav className="hidden md:flex items-center gap-6 text-sm text-white/80">
            <Link className="hover:text-white" to="/marketplace">
              Marketplace
            </Link>
            <Link className="hover:text-white" to="/pricing">
              Pricing
            </Link>
            <Link className="hover:text-white" to="/faq">
              FAQ
            </Link>
            <Link className="hover:text-white" to="/auth/login">
              Log in
            </Link>
            <Link className="hover:text-white" to="/auth/register">
              Register
            </Link>
          </nav>

          <button
            type="button"
            className="md:hidden rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            aria-label="Open menu"
            aria-expanded={menuOpen}
            aria-controls="mobile-menu"
            onClick={() => setMenuOpen((v) => !v)}
          >
            ☰
          </button>
        </div>

        {menuOpen && (
          <>
            <button
              type="button"
              className="fixed inset-0 z-40 bg-black/30 md:hidden"
              aria-label="Close menu"
              onClick={closeMenu}
            />
            <div
              id="mobile-menu"
              className="absolute right-0 top-full mt-2 w-56 rounded-xl bg-neutral-900/95 border border-white/10 shadow-xl z-50 md:hidden"
            >
              <nav className="flex flex-col p-2 text-sm">
                <Link
                  className="rounded-lg px-3 py-2 hover:bg-white/10"
                  to="/"
                  onClick={closeMenu}
                >
                  Home
                </Link>
                <Link
                  className="rounded-lg px-3 py-2 hover:bg-white/10"
                  to="/marketplace"
                  onClick={closeMenu}
                >
                  Marketplace
                </Link>
                <Link
                  className="rounded-lg px-3 py-2 hover:bg-white/10"
                  to="/pricing"
                  onClick={closeMenu}
                >
                  Pricing
                </Link>
                <Link
                  className="rounded-lg px-3 py-2 hover:bg-white/10"
                  to="/faq"
                  onClick={closeMenu}
                >
                  FAQ
                </Link>
                <Link
                  className="rounded-lg px-3 py-2 hover:bg-white/10"
                  to="/auth/login"
                  onClick={closeMenu}
                >
                  Log in
                </Link>
                <Link
                  className="rounded-lg px-3 py-2 hover:bg-white/10"
                  to="/auth/register"
                  onClick={closeMenu}
                >
                  Register
                </Link>
              </nav>
            </div>
          </>
        )}
      </div>
    </header>
  );
}

