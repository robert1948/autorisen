import React from "react";

import { LandingTemplate, type LandingContent } from "./LandingTemplate";

import landingMobile from "../../../../design/json/landing.mobile.json";

export default function LandingMobilePage() {
  return <LandingTemplate content={landingMobile as LandingContent} />;
}
