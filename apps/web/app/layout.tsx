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

export const metadata: Metadata = {
  title: "Advance Astro",
  description: "Private, local-first astrology insights."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

