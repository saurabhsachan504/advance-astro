import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Advance Astro",
  description: "Private, local-first astrology insights."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

