import type { Metadata } from "next";
import "./styles.css";
import "./dual-insight.css";
import "./systems.css";
import "./navigation.css";
import "./light-premium.css";
import "./advanced/advanced.css";
import "./advanced-link.css";
import "./advanced/pro/pro.css";
import "./ashtakavarga.css";
import "./premium-ui.css";
import "./noir-copper.css";
import "./light-clarity.css";
import "./hero-mobile.css";
import "./language.css";
import "./location-search.css";
import "./studios.css";
import "./timeline.css";
import "./traditional-kundli.css";
import LanguageToggle from "./language-toggle";
import LocationSearch from "./location-search";

export const metadata: Metadata = {
  title: "Advance Astro",
  description: "Private, local-first astrology insights."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}<LocationSearch /><LanguageToggle /></body></html>;
}

