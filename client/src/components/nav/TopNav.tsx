import logoUrl from "../../assets/capecontrol-logo.png";
import { Link } from "react-router-dom";

type Props = {
  onOpenSupport: () => void;
};

const TopNav = ({ onOpenSupport }: Props) => {
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
      <div className="top-nav__actions">
        <nav className="top-nav__nav-links">
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
          <a href="#faq">FAQ</a>
        </nav>
        <div className="top-nav__auth">
          <a className="link" href="#auth">
            Login
          </a>
          <Link className="btn btn--ghost" to="/register">
            Register
          </Link>
          <button type="button" onClick={onOpenSupport} className="btn btn--primary">
            Support
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
