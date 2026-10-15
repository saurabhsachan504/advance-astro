"use client";

import { FormEvent, useState } from "react";

type Planet = { name: string; longitude: number; sign: string; nakshatra: string };
type Chart = { ascendant: Planet; planets: Planet[]; provenance: { engine_version: string; ephemeris_version: string } };

// Same-origin proxy keeps the private API inside Docker's internal network.
const API = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export default function Home() {
  const [chart, setChart] = useState<Chart | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  async function createChart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setStatus("Calculating deterministic chart facts…");
    const form = new FormData(event.currentTarget);
    const payload = {
      birth_datetime: form.get("birth_datetime"), timezone: form.get("timezone"),
      latitude: Number(form.get("latitude")), longitude: Number(form.get("longitude")), ayanamsa: "lahiri"
    };
    try {
      const response = await fetch(`${API}/api/v1/charts/calculate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      if (!response.ok) throw new Error((await response.json()).detail || "Unable to calculate chart");
      setChart(await response.json()); setStatus("Chart calculated locally by the astronomy engine.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unknown error"); setStatus(""); }
  }

  return <main>
    <header><div className="brand">✦ ADVANCE ASTRO</div><div className="pill">Private • Local-first • Rule-grounded</div></header>
    <section className="hero">
      <div><p className="eyebrow">YOUR COSMIC BLUEPRINT</p><h1>Insight, rooted in <em>exact</em> celestial math.</h1><p className="intro">A private astrology workspace where astronomical chart facts always come before interpretation.</p></div>
      <div className="orb" aria-hidden="true"><span>✦</span></div>
    </section>
    <section className="grid">
      <form className="card" onSubmit={createChart}>
        <p className="eyebrow">01 / BIRTH DETAILS</p><h2>Generate your kundli</h2>
        <label>Local birth date & time<input required name="birth_datetime" type="datetime-local" defaultValue="1995-08-15T10:30" /></label>
        <label>IANA time zone<input required name="timezone" defaultValue="Asia/Kolkata" placeholder="Asia/Kolkata" /></label>
        <div className="two"><label>Latitude<input required name="latitude" type="number" step="any" defaultValue="28.6139" /></label><label>Longitude<input required name="longitude" type="number" step="any" defaultValue="77.2090" /></label></div>
        <button type="submit">Calculate chart <span>→</span></button>
        {status && <p className="success">{status}</p>}{error && <p className="error">{error}</p>}
      </form>
      <aside className="card insight"><p className="eyebrow">02 / DUAL INSIGHT</p><h2>Palm & face — optional</h2><p>When enabled later, photos are processed locally with explicit consent and automatic deletion. This never identifies you or makes medical or guaranteed predictions.</p><div className="privacy-note">◌ Raw photo default: delete after analysis<br/>◌ Visual symbolism shown separately from chart facts</div><button type="button" className="secondary" disabled>Connect after chart creation</button></aside>
    </section>
    {chart && <section className="results"><div><p className="eyebrow">CALCULATION RESULT</p><h2>Chart facts</h2><p className="muted">Engine {chart.provenance.engine_version} · Ephemeris {chart.provenance.ephemeris_version}</p></div><div className="facts"><article className="asc"><small>ASCENDANT</small><strong>{chart.ascendant.sign}</strong><span>{chart.ascendant.longitude.toFixed(2)}° · {chart.ascendant.nakshatra}</span></article>{chart.planets.map((planet) => <article key={planet.name}><small>{planet.name.toUpperCase()}</small><strong>{planet.sign}</strong><span>{planet.longitude.toFixed(2)}° · {planet.nakshatra}</span></article>)}</div></section>}
    <footer>Astrology is spiritual/entertainment guidance, not scientific, medical, financial, or legal advice.</footer>
  </main>;
}

