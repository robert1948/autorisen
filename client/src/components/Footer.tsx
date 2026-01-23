import React from 'react';
import { Link } from "react-router-dom";
import logoUrl from "../assets/capecontrol-logo.png";
import { APP_VERSION } from "../version";

type Props = {
  onOpenSupport: () => void;
};

const Footer: React.FC<Props> = ({ onOpenSupport }) => {
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
                <Link to="/how-it-works">How It Works</Link>
              </li>
              <li>
                <Link to="/explore">Workflows</Link>
              </li>
            </ul>
          </div>

          <div className="footer__column">
            <h4>Developers</h4>
            <ul className="footer__links-list">
              <li>
                <Link to="/developer-hub">Developer Hub</Link>
              </li>
              <li>
                <Link to="/developer-hub">Join as Developer</Link>
              </li>
              <li>
                <Link to="/api-docs">API Documentation</Link>
              </li>
            </ul>
          </div>

          <div className="footer__column">
            <h4>Company</h4>
            <ul className="footer__links-list">
              <li>
                <Link to="/auth/register">Create free account</Link>
              </li>
              <li>
                <Link to="/how-it-works">About Us</Link>
              </li>
              <li>
                <Link to="/contact" className="footer__link-button" onClick={onOpenSupport}>
                  Contact
                </Link>
              </li>
              <li>
                <Link to="/privacy">Privacy Policy</Link>
              </li>
              <li>
                <Link to="/terms">Terms of Service</Link>
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
