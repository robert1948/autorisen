type Props = {
  onOpenSupport: () => void;
};

const TopNav = ({ onOpenSupport }: Props) => {
  return (
    <header className="top-nav" id="top">
      <div className="top-nav__brand">
        <span className="top-nav__title">Autorisen</span>
      </div>
      <div className="top-nav__actions">
        <nav className="top-nav__nav-links">
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
          <a href="#faq">FAQ</a>
        </nav>
        <div className="top-nav__auth">
          <a className="link" href="#login">
            Login
          </a>
          <a className="btn btn--ghost" href="#register">
            Register
          </a>
          <button type="button" onClick={onOpenSupport} className="btn btn--primary">
            Support
          </button>
        </div>
      </div>
    </header>
  );
};

export default TopNav;
