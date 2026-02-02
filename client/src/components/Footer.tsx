import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import logoUrl from "../assets/capecontrol-logo.png";
import { APP_VERSION } from "../version";

type Props = {
  onOpenSupport: () => void;
};

const Footer: React.FC<Props> = ({ onOpenSupport }) => {
  const [backendVersion, setBackendVersion] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    fetch("/api/version", { cache: "no-store" })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        const value = typeof data?.version === "string" ? data.version.trim() : "";
        if (!isMounted) return;
        setBackendVersion(value.length > 0 ? value : null);
      })
      .catch(() => {
        if (!isMounted) return;
        setBackendVersion(null);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <footer className="footer">
      <div className="footer__content">
        <div className="footer__main">
          <div className="footer__brand">
            <img
              className="footer__logo"
              src={logoUrl}
              alt="CapeControl logo"
              width={44}
              height={44}
              loading="lazy"
            />
            <div>
              <h3>CapeControl</h3>
              <div className="footer__legal-desktop">
                <p>
                  Workflow-first AI platform that helps small businesses and growing teams run more
                  smoothly, with enterprise-grade security behind the scenes.
                </p>
                <p className="footer__brand-meta">Operated by Cape Craft Projects CC (VAT: 4270105119)</p>
                <p className="footer__brand-meta">Trading as CapeControl</p>
                <p className="footer__brand-meta">Empowering AI-driven operations worldwide</p>
              </div>
              <p className="footer__legal-mobile">
                CapeControl • Operated by Cape Craft Projects CC (VAT: 4270105119)
              </p>
            </div>
          </div>

          <div className="footer__column">
            <h4>Platform</h4>
            <ul className="footer__links-list">
              <li>
                <Link to="/">Overview</Link>
              </li>
              <li>
                <Link to="/marketplace">Marketplace</Link>
              </li>
              <li>
                <Link to="/pricing">Pricing</Link>
              </li>
              <li>
                <Link to="/faq">FAQ</Link>
              </li>
            </ul>
          </div>

          <div className="footer__column">
            <h4>Account</h4>
            <ul className="footer__links-list">
              <li>
                <Link to="/auth/login">Log in</Link>
              </li>
              <li>
                <Link to="/auth/register">Create free account</Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="footer__bottom">
          <p>© {new Date().getFullYear()} CapeControl. All rights reserved.</p>
          <div className="footer__bottom-meta">
            <span>Built with ❤️ for operators and their teams.</span>
            <span
              data-testid="app-version"
              className="ml-3 font-mono text-xs text-slate-200/90"
            >
              v{APP_VERSION}
            </span>
            {backendVersion && (
              <span
                data-testid="backend-version"
                title={backendVersion}
                className="ml-3 font-mono text-xs text-slate-200/90"
              >
                backend:{backendVersion.slice(0, 12)}
              </span>
            )}
            <span className="footer__status">
              <span className="footer__status-dot" aria-hidden="true" />
              All systems operational
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
