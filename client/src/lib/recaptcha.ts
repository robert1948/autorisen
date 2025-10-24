let loaded: Promise<void> | null = null;

function load(siteKey: string): Promise<void> {
  if (loaded) return loaded;
  loaded = new Promise((resolve, reject) => {
    if ((window as any).grecaptcha?.enterprise) return resolve();
    const s = document.createElement("script");
    s.src = `https://www.google.com/recaptcha/enterprise.js?render=${siteKey}`;
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error("Failed to load reCAPTCHA Enterprise"));
    document.head.appendChild(s);
  });
  return loaded;
}

export async function recaptchaToken(action: string): Promise<string> {
  const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY as string;
  if (!siteKey) return ""; // allow disabled builds
  await load(siteKey);
  // @ts-ignore
  const gre = (window as any).grecaptcha.enterprise;
  await new Promise<void>((r) => gre.ready(() => r()));
  return await gre.execute(siteKey, { action });
}
