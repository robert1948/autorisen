import { useEffect, useRef } from "react";
import ReCAPTCHA from "react-google-recaptcha";

type RecaptchaProps = {
  onVerify: (token: string | null) => void;
  error?: string;
};

const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY as string | undefined;

const Recaptcha = ({ onVerify, error }: RecaptchaProps) => {
  const hasBypassed = useRef(false);
  const latestOnVerify = useRef(onVerify);

  useEffect(() => {
    latestOnVerify.current = onVerify;
  }, [onVerify]);

  useEffect(() => {
    if (!siteKey && !hasBypassed.current) {
      hasBypassed.current = true;
      latestOnVerify.current("dev-bypass-token");
    }
  }, []);

  if (!siteKey) {
    // Bypass token already supplied via useEffect; render nothing visible
    return null;
  }

  return (
    <div className={`recaptcha-field ${error ? "recaptcha-field--error" : ""}`}>
      <ReCAPTCHA sitekey={siteKey} onChange={onVerify} onExpired={() => onVerify(null)} />
      {error && <p className="recaptcha-field__error">{error}</p>}
    </div>
  );
};

export default Recaptcha;
