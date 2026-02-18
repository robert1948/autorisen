import logoUrl from "../../assets/capecontrol-logo.png";
import { Link, useLocation } from "react-router-dom";
import { useState } from "react";

type Props = {
  onOpenSupport: () => void;
};

const TopNav = ({ onOpenSupport: _onOpenSupport }: Props) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { search } = useLocation();
  const registerHref = `/auth/register${search}`;

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
          width={72}
          height={72}
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
        <div className="top-nav__auth">
          <Link className="link" to="/auth/login" onClick={closeMenu}>
            Login
          </Link>
          <Link className="btn btn--ghost" to={registerHref} onClick={closeMenu}>
            Register
          </Link>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
