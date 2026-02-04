import React from 'react';
import logoUrl from "../assets/capecontrol-logo.png";
import BuildBadge from "./version/BuildBadge";

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
                <a href="#home">Overview</a>
              </li>
              <li>
                <a href="#experiences">How It Works</a>
              </li>
              <li>
                <a href="#features">Workflows</a>
              </li>
            </ul>
          </div>

          <div className="footer__column">
            <h4>Developers</h4>
            <ul className="footer__links-list">
              <li>
                <a href="#developers">Developer Hub</a>
              </li>
              <li>
                <a href="#experiences">Join as Developer</a>
              </li>
              <li>
                <a href="#developers">API Documentation</a>
              </li>
            </ul>
          </div>

          <div className="footer__column">
            <h4>Company</h4>
            <ul className="footer__links-list">
              <li>
                <a href="#about">About Us</a>
              </li>
              <li>
                <button
                  type="button"
                  className="footer__link-button"
                  onClick={onOpenSupport}
                >
                  Contact
                </button>
              </li>
              <li>
                <a href="#privacy">Privacy Policy</a>
              </li>
              <li>
                <a href="#terms">Terms of Service</a>
              </li>
            </ul>
          </div>
        </div>

        <div className="footer__bottom">
          <p>© {new Date().getFullYear()} CapeControl. All rights reserved.</p>
          <div className="footer__bottom-meta">
            <span>Built with ❤️ for operators and their teams.</span>
            <span>v{__APP_VERSION__}</span>
            <span className="footer__status">
              <span className="footer__status-dot" aria-hidden="true" />
              All systems operational
            </span>
            <BuildBadge />
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
