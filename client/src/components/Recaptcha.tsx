import { useEffect } from "react";
import ReCAPTCHA from "react-google-recaptcha";

type RecaptchaProps = {
  onVerify: (token: string | null) => void;
  error?: string;
};

const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY as string | undefined;

const Recaptcha = ({ onVerify, error }: RecaptchaProps) => {
  useEffect(() => {
    if (!siteKey) {
      onVerify("dev-bypass-token");
    }
  }, [onVerify]);

  if (!siteKey) {
    return (
      <div className="recaptcha-placeholder">
        <p className="recaptcha-placeholder__info">
          reCAPTCHA is not configured. Set <code>VITE_RECAPTCHA_SITE_KEY</code> when you are ready to
          enforce verification. A temporary bypass token has been supplied for local testing.
        </p>
      </div>
    );
  }

  return (
    <div className={`recaptcha-field ${error ? "recaptcha-field--error" : ""}`}>
      <ReCAPTCHA sitekey={siteKey} onChange={onVerify} onExpired={() => onVerify(null)} />
      {error && <p className="recaptcha-field__error">{error}</p>}
    </div>
  );
};

export default Recaptcha;
