import { Link, useLocation } from "react-router-dom";

import AuthForms from "../features/auth/AuthForms";
import Footer from "../components/Footer";
import logoUrl from "../assets/capecontrol-logo.png";

const Login = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const emailVerifiedBanner = params.get("email_verified") === "1";
  const handleOpenSupport = () => undefined;

  return (
    <>
      <div className="auth-page">
        <header className="auth-page__brand">
          <Link to="/" className="auth-page__brand-link">
            <img
              src={logoUrl}
              alt="CapeControl"
              width={42}
              height={42}
              loading="lazy"
              className="auth-page__brand-logo"
            />
            <span className="auth-page__brand-name">CapeControl</span>
          </Link>
          <Link to="/auth/register" className="auth-page__brand-cta">
            Create account
          </Link>
        </header>
        {emailVerifiedBanner && (
          <p className="auth-banner auth-banner--success">Email verified! You can sign in now.</p>
        )}
        <AuthForms />
      </div>
      <Footer onOpenSupport={handleOpenSupport} />
    </>
  );
};

export default Login;
