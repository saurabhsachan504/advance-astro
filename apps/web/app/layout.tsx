import type { Metadata } from "next";
import "./styles.css";
import "./dual-insight.css";
import "./systems.css";
import "./navigation.css";
import "./light-premium.css";

export const metadata: Metadata = {
  title: "Advance Astro",
  description: "Private, local-first astrology insights."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

