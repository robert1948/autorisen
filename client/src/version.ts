declare const __APP_VERSION__: string | undefined;

const injectedVersion = typeof __APP_VERSION__ !== "undefined" ? __APP_VERSION__ : undefined;
const normalizedVersion = (injectedVersion ?? "").trim();

export const APP_VERSION = normalizedVersion.length > 0 ? normalizedVersion : "0.0.0";
