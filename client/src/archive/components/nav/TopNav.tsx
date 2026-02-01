/**
 * ARCHIVED: Legacy top navigation (anchor-link marketing shell).
 * Do not import or route to this component.
 */

import { Link } from "react-router-dom";
import { useState } from "react";

import logoUrl from "../../assets/CapeControl_Logo_Transparent.png";

const TopNav = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <header className="top-nav" id="top">
      <Link
        to="/"
        className="top-nav__brand"
        onClick={closeMenu}
        aria-label="CapeControl"
      >
        <img
          className="top-nav__logo"
          src={logoUrl}
          alt="CapeControl"
          loading="lazy"
          style={{ height: 34, width: "auto" }}
        />
      </Link>
      
      <button 
        className="top-nav__hamburger"
        onClick={toggleMenu}
        aria-label="Toggle navigation menu"
        aria-expanded={isMenuOpen}
      >
        <span className={`top-nav__hamburger-line ${isMenuOpen ? 'top-nav__hamburger-line--open' : ''}`}></span>
        <span className={`top-nav__hamburger-line ${isMenuOpen ? 'top-nav__hamburger-line--open' : ''}`}></span>
        <span className={`top-nav__hamburger-line ${isMenuOpen ? 'top-nav__hamburger-line--open' : ''}`}></span>
      </button>

      <div className={`top-nav__actions ${isMenuOpen ? 'top-nav__actions--open' : ''}`}>
        <nav className="top-nav__nav-links">
          <a href="#home" onClick={closeMenu}>Home</a>
          <a href="#features" onClick={closeMenu}>Features</a>
          <a href="#experiences" onClick={closeMenu}>Experiences</a>
        </nav>
        <div className="top-nav__auth">
          <Link className="link" to="/auth/register" onClick={closeMenu}>
            Create free account
          </Link>
          <Link className="link" to="/auth/login" onClick={closeMenu}>
            Log in
          </Link>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
