import logoUrl from "../../assets/capecontrol-logo.png";
import { Link } from "react-router-dom";
import { useState } from "react";

type Props = {
  onOpenSupport: () => void;
};

const TopNav = ({ onOpenSupport }: Props) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <header className="top-nav" id="top">
      <div className="top-nav__brand">
        <img
          className="top-nav__logo"
          src={logoUrl}
          alt="CapeControl logo"
          width={48}
          height={48}
          loading="lazy"
        />
        <span className="top-nav__title">CapeControl</span>
      </div>
      
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
          <a href="#pricing" onClick={closeMenu}>Pricing</a>
          <a href="#faq" onClick={closeMenu}>FAQ</a>
        </nav>
        <div className="top-nav__auth">
          <Link className="link" to="/login" onClick={closeMenu}>
            Login
          </Link>
          <Link className="btn btn--ghost" to="/register" onClick={closeMenu}>
            Register
          </Link>
          <button type="button" onClick={() => { onOpenSupport(); closeMenu(); }} className="btn btn--primary">
            Support
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
