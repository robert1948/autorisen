import React from "react";

import { LandingTemplate, type LandingContent } from "./LandingTemplate";

import landingDesktop from "../../../../design/json/landing.desktop.json";

export default function LandingDesktopPage() {
  return <LandingTemplate content={landingDesktop as LandingContent} />;
}
