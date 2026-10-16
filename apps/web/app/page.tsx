"use client";

import { ChangeEvent, FormEvent, useEffect, useState } from "react";
import "./dual-insight.css";

type Planet = { name: string; longitude: number; sign: string; nakshatra: string };
type Chart = { ascendant: Planet; planets: Planet[]; provenance: { engine_version: string; ephemeris_version: string } };

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "";
const SIGNS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];

function Sparkle() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 1.8c.54 6.05 3.55 9.06 9.6 9.6-6.05.54-9.06 3.55-9.6 9.6-.54-6.05-3.55-9.06-9.6-9.6 6.05-.54 9.06-3.55 9.6-9.6Z" /></svg>; }
function Arrow() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" /></svg>; }
function Lock() { return <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>; }

function OrbitalChart({ chart }: { chart: Chart | null }) {
  const labels = chart ? [chart.ascendant, ...chart.planets.slice(0, 6)] : null;
  return <div className="orbit-wrap" aria-label="Chart visualisation">
    <div className="orbit orbit-1"/><div className="orbit orbit-2"/><div className="orbit orbit-3"/>
    <div className="orbit-core"><span>{chart ? chart.ascendant.sign.slice(0, 3) : "ॐ"}</span><small>{chart ? "ASC" : "VEDA"}</small></div>
    {labels ? labels.map((planet, index) => <div key={planet.name} className={`planet p-${index}`}><b>{planet.name === "Ascendant" ? "As" : planet.name.slice(0, 2)}</b></div>) : <><div className="planet p-0"><b>Su</b></div><div className="planet p-1"><b>Mo</b></div><div className="planet p-2"><b>Ma</b></div><div className="planet p-3"><b>Ve</b></div><div className="planet p-4"><b>Ju</b></div></>}
  </div>;
}

export default function Home() {
  const [chart, setChart] = useState<Chart | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [visualFile, setVisualFile] = useState<File | null>(null);
  const [visualSubject, setVisualSubject] = useState<"palm" | "face">("palm");
  const [visualReading, setVisualReading] = useState("");
  const [visualError, setVisualError] = useState("");
  const [visualLoading, setVisualLoading] = useState(false);
  const [forecastStatus, setForecastStatus] = useState("");
  const [forecastError, setForecastError] = useState("");

  useEffect(() => {
    const saved = window.localStorage.getItem("veda-theme");
    const nextTheme = saved === "light" || saved === "dark" ? saved : window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    setTheme(nextTheme);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("veda-theme", theme);
  }, [theme]);

  async function createChart(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setStatus(""); setLoading(true);
    const form = new FormData(event.currentTarget);
    const payload = { birth_datetime: form.get("birth_datetime"), timezone: form.get("timezone"), latitude: Number(form.get("latitude")), longitude: Number(form.get("longitude")), ayanamsa: "lahiri" };
    try {
      const response = await fetch(`${API}/api/v1/charts/calculate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const body = await response.text();
      if (!response.ok) { try { throw new Error(JSON.parse(body).detail || "Unable to calculate chart"); } catch (reason) { if (reason instanceof SyntaxError) throw new Error("Chart engine is unavailable. Start the local Docker stack to calculate."); throw reason; } }
      setChart(JSON.parse(body)); setStatus("Celestial positions calculated by the local ephemeris engine.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to calculate chart"); } finally { setLoading(false); }
  }

  function chooseVisualFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] || null;
    setVisualFile(file); setVisualReading(""); setVisualError("");
  }

  async function analyseVisual() {
    if (!visualFile) { setVisualError(`Choose a clear ${visualSubject} photo first.`); return; }
    setVisualError(""); setVisualLoading(true);
    const form = new FormData();
    form.append("image", visualFile); form.append("subject", visualSubject); form.append("consent_visual_analysis", "true");
    try {
      const response = await fetch(`${API}/api/v1/visual-readings`, { method: "POST", body: form });
      const body = await response.text();
      if (!response.ok) { try { throw new Error(JSON.parse(body).detail || "Visual reading unavailable"); } catch (reason) { if (reason instanceof SyntaxError) throw new Error("Local vision service is unavailable."); throw reason; } }
      setVisualReading(JSON.parse(body).interpretation);
    } catch (reason) { setVisualError(reason instanceof Error ? reason.message : "Visual reading unavailable"); } finally { setVisualLoading(false); }
  }

  async function saveForecast(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setForecastError(""); setForecastStatus("");
    const form = new FormData(event.currentTarget);
    try {
      const response = await fetch(`${API}/api/v1/forecasts`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ profile_reference: "local-demo-profile", prediction: form.get("prediction"), rule_key: form.get("rule_key"), due_at: form.get("due_at"), contact_address: null }) });
      const body = await response.text();
      if (!response.ok) { try { throw new Error(JSON.parse(body).detail || "Unable to save forecast"); } catch (reason) { if (reason instanceof SyntaxError) throw new Error("Feedback memory is unavailable."); throw reason; } }
      setForecastStatus("Forecast saved. On the due date, request feedback before treating it as evidence."); event.currentTarget.reset();
    } catch (reason) { setForecastError(reason instanceof Error ? reason.message : "Unable to save forecast"); }
  }

  return <main>
    <div className="sky-noise" aria-hidden="true"/>
    <nav><a className="brand" href="#top"><span className="brand-mark"><Sparkle /></span><span>VEDA<span className="brand-light">/OS</span></span></a><div className="nav-center"><a href="#chart">Birth chart</a><a href="#insight">Dual insight <i>new</i></a><a href="#privacy">Privacy</a></div><div className="nav-actions"><span className="online"><i/> Engine online</span><button className="theme-toggle" type="button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}><span>{theme === "dark" ? "☾" : "☼"}</span><i/></button><button className="avatar" aria-label="Profile">VS</button></div></nav>
    <section id="top" className="hero"><div className="hero-copy"><p className="kicker"><span><Sparkle /></span> PRIVATE ASTRO INTELLIGENCE</p><h1>Your universe,<br/><em>rendered precisely.</em></h1><p className="hero-text">A private observatory for the patterns written in your birth moment—built on astronomical math, not guesswork.</p><div className="hero-meta"><span><b>01</b> Exact ephemeris</span><span><b>02</b> Local-first data</span><span><b>03</b> Your language</span></div></div><div className="hero-object"><div className="horizon-label top-label">S I D E R E A L &nbsp; / &nbsp; L A H I R I</div><OrbitalChart chart={chart}/><div className="horizon-label bottom-label">{chart ? `${chart.ascendant.sign} RISING` : "A PERSONAL COSMOS"}</div><div className="corner-note">{chart ? "LIVE CHART" : "EST. 2026"}</div></div></section>
    <section className="dashboard"><form id="chart" className="birth-card glass-card" onSubmit={createChart}><div className="card-heading"><div><p className="section-index">01 — CREATE CHART</p><h2>Find your celestial<br/>blueprint.</h2></div><div className="moon-phase" aria-hidden="true"><span/></div></div><div className="form-rule"/><div className="field-grid"><label className="wide"><span>Birth date &amp; time</span><input required name="birth_datetime" type="datetime-local" defaultValue="1995-08-15T10:30" /></label><label><span>Latitude</span><input required name="latitude" type="number" step="any" defaultValue="28.6139" /></label><label><span>Longitude</span><input required name="longitude" type="number" step="any" defaultValue="77.2090" /></label><label className="wide"><span>IANA time zone</span><input required name="timezone" defaultValue="Asia/Kolkata" placeholder="Asia/Kolkata" /></label></div><button className="primary-button" type="submit" disabled={loading}>{loading ? "Calculating your sky…" : <><span>Reveal my chart</span><Arrow /></>}</button><p className="form-foot"><Lock/> Your birth data stays in your private workspace.</p>{status && <p className="message success">✦ {status}</p>}{error && <p className="message error">{error}</p>}</form>
      <aside id="insight" className="insight-card"><div className="card-orbit"><span>✦</span></div><p className="section-index">02 — DUAL INSIGHT</p><h2>One chart.<br/><em>Many signals.</em></h2><p>Pair chart mathematics with optional palm or face symbolism for a layered spiritual reading.</p><div className="insight-list"><div><span>01</span><b>Kundli facts</b><i>{chart ? "Ready" : "First"}</i></div><div><span>02</span><b>Visual symbolism</b><i>Opt-in</i></div><div><span>03</span><b>Cross-match</b><i>Interpretive</i></div></div><div className="visual-controls"><div className="visual-tabs"><button className={visualSubject === "palm" ? "active" : ""} type="button" onClick={() => setVisualSubject("palm")}>Palm</button><button className={visualSubject === "face" ? "active" : ""} type="button" onClick={() => setVisualSubject("face")}>Face</button></div><label className="upload-box"><input type="file" accept="image/jpeg,image/png,image/webp" onChange={chooseVisualFile}/><span>{visualFile ? visualFile.name : `Choose ${visualSubject} photo`}</span><b>Browse</b></label><button type="button" className="visual-button" onClick={analyseVisual} disabled={visualLoading}>{visualLoading ? "Reading image…" : `Analyse ${visualSubject}`}</button><small>By continuing, you consent to local image analysis. Raw photos are not stored.</small>{visualReading && <div className="visual-result"><b>Visual symbols</b><p>{visualReading}</p>{chart && <span>✦ Chart facts are available for your next interpretive report.</span>}</div>}{visualError && <p className="visual-error">{visualError}</p>}</div></aside></section>
    {chart ? <><section className="results-panel"><div className="results-title"><p className="section-index">YOUR COSMIC SNAPSHOT</p><h2>The sky at your<br/><em>first breath.</em></h2><p>Calculated in sidereal Lahiri using the Swiss Ephemeris engine.</p></div><div className="sign-wheel"><div className="wheel-ring">{SIGNS.map((sign, i) => <span key={sign} style={{ transform: `rotate(${i * 30}deg) translateY(-104px) rotate(${-i * 30}deg)` }}>{sign}</span>)}</div><div className="wheel-center"><b>{chart.ascendant.sign}</b><small>ASCENDANT</small></div></div><div className="planet-list">{chart.planets.map((planet, index) => <div key={planet.name} className="planet-row"><span className="planet-number">0{index + 1}</span><b>{planet.name}</b><span>{planet.sign}</span><span>{planet.longitude.toFixed(2)}°</span><i>{planet.nakshatra}</i></div>)}</div></section><section className="feedback-lab"><div><p className="section-index">03 — CALIBRATION MEMORY</p><h2>Keep insight<br/><em>accountable.</em></h2><p>Save a time-bound interpretation, then collect voluntary feedback later. Feedback creates evidence—not a guarantee.</p></div><form onSubmit={saveForecast}><label><span>Interpretive forecast</span><textarea required name="prediction" minLength={12} placeholder="Example: Career momentum may increase over the next month…"/></label><div className="forecast-row"><label><span>Rule label</span><input required name="rule_key" defaultValue="career-10th-11th"/></label><label><span>Review date</span><input required name="due_at" type="datetime-local"/></label></div><button type="submit" className="feedback-button">Save for feedback <Arrow/></button>{forecastStatus && <p className="feedback-success">✦ {forecastStatus}</p>}{forecastError && <p className="feedback-error">{forecastError}</p>}</form></section></> : <section className="placeholder-panel"><div><p className="section-index">WHEN YOU ARE READY</p><h2>Your chart will unfold here.</h2></div><p>Enter the moment and place of birth above. Every position is calculated from local ephemeris data, with transparent provenance.</p><div className="placeholder-stars"><Sparkle/><Sparkle/><Sparkle/></div></section>}
    <section id="privacy" className="privacy-strip"><div className="privacy-icon"><Lock/></div><div><p className="section-index">PRIVATE BY DESIGN</p><h3>Your story does not leave your orbit.</h3></div><p>We separate deterministic chart calculation from interpretation, and make visual analysis opt-in with a delete-first policy.</p><a href="#top">Privacy architecture <Arrow /></a></section><footer><div className="brand"><span className="brand-mark"><Sparkle /></span><span>VEDA<span className="brand-light">/OS</span></span></div><p>Astrology is spiritual guidance, not medical, legal or financial advice.</p><span>© 2026 ADVANCE ASTRO</span></footer>
  </main>;
}
