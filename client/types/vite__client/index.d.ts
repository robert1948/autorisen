interface ImportMetaEnv {
  readonly VITE_API_BASE?: string;
  readonly VITE_RECAPTCHA_SITE_KEY?: string;
  readonly VITE_ENABLE_CHATKIT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module "vite/client" {
  interface ImportMetaEnv {
    readonly VITE_API_BASE?: string;
    readonly VITE_RECAPTCHA_SITE_KEY?: string;
    readonly VITE_ENABLE_CHATKIT?: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}
