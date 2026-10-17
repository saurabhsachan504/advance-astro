"use client";

import { Component, FormEvent, ReactNode, useEffect, useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "";
type Data = Record<string, unknown>;
const record = (value: unknown): Data => value !== null && typeof value === "object" && !Array.isArray(value) ? value as Data : {};
const records = (value: unknown): Data[] => Array.isArray(value) ? value.map(record) : [];
const text = (value: unknown, fallback = "—"): string => typeof value === "string" || typeof value === "number" ? String(value) : fallback;
const localMoment = (timezone: string) => new Intl.DateTimeFormat("sv-SE", { timeZone: timezone, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23" }).format(new Date()).replace(" ", "T");
const tools = [
  ["dasha", "Dasha timeline", "Maha and Antardasha periods"], ["kundli", "Kundli studio", "D1, D9 and D10 chart data"],
  ["calendar", "Astro calendar", "Panchang, Rahu Kaal and eclipse alerts"], ["muhurat", "Muhurat planner", "Event time-window baseline"],
  ["gochar", "Live Gochar", "Current transits and Sade Sati phase"], ["strengths", "Ashtakavarga lab", "Bhinna, Sarva and bala components"],
  ["prashna", "Prashna Kundli", "Question-time chart facts"], ["match", "Matchmaking", "Ashtakoota, KP and synastry"],
] as const;

export default function ProAdvancedTools() {
  const form = useRef<HTMLFormElement>(null); const [result, setResult] = useState<Data | null>(null); const [active, setActive] = useState("welcome"); const [error, setError] = useState(""); const [loading, setLoading] = useState(false); const [theme, setTheme] = useState<"dark" | "light">("dark");
  useEffect(() => { const saved = window.localStorage.getItem("veda-theme"); setTheme(saved === "light" || saved === "dark" ? saved : window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"); }, []);
  useEffect(() => { document.documentElement.dataset.theme = theme; window.localStorage.setItem("veda-theme", theme); }, [theme]);
  const profile = () => { const data = new FormData(form.current!); return { birth_datetime: data.get("birth_datetime"), timezone: data.get("timezone"), latitude: Number(data.get("latitude")), longitude: Number(data.get("longitude")), ayanamsa: "lahiri" }; };
  const run = async (kind: string) => {
    const base = profile(); const formData = new FormData(form.current!); setActive(kind); setError(""); setLoading(true);
    let path = ""; let payload: Data = base;
    if (kind === "dasha") { path = "/dasha/vimshottari"; payload = { ...base, years: 20 }; }
    if (kind === "kundli") { path = "/kundli/interactive"; payload = { ...base, layout: "north_indian" }; }
    if (kind === "calendar") { path = "/calendar/panchang"; payload = { date: String(base.birth_datetime).slice(0, 10), timezone: base.timezone, latitude: base.latitude, longitude: base.longitude }; }
    if (kind === "muhurat") { path = "/muhurat/plan"; payload = { date: String(base.birth_datetime).slice(0, 10), timezone: base.timezone, latitude: base.latitude, longitude: base.longitude, event: formData.get("event"), end_date: String(base.birth_datetime).slice(0, 10) }; }
    if (kind === "gochar") { path = "/gochar/live"; payload = base; }
    if (kind === "strengths") { path = "/strengths/calculate"; }
    if (kind === "prashna") { path = "/prashna/calculate"; payload = { question: formData.get("question") || "What should I understand from this moment?", question_datetime: localMoment(String(base.timezone)), timezone: base.timezone, latitude: base.latitude, longitude: base.longitude }; }
    if (kind === "match") { path = "/matchmaking/analyse"; payload = { person_a: base, person_b: { birth_datetime: formData.get("match_birth_datetime"), timezone: formData.get("match_timezone"), latitude: Number(formData.get("match_latitude")), longitude: Number(formData.get("match_longitude")), ayanamsa: "lahiri" }, person_a_label: "Profile A", person_b_label: "Profile B" }; }
    try {
      const response = await fetch(`${API}/api/v1${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const body = await response.text();
      let parsed: unknown;
      try { parsed = JSON.parse(body); } catch { throw new Error("Calculation returned an invalid response. Please try again."); }
      if (!response.ok) throw new Error(text(record(parsed).detail, "Calculation unavailable"));
      setResult(record(parsed));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Calculation unavailable"); } finally { setLoading(false); }
  };
  const pdf = async () => { const response = await fetch(`${API}/api/v1/reports/chart.pdf`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...profile(), report_title: "Private Advance Astro Chart Report" }) }); if (!response.ok) { setError("PDF report is unavailable."); return; } const link = document.createElement("a"); link.href = URL.createObjectURL(await response.blob()); link.download = "advance-astro-chart.pdf"; link.click(); URL.revokeObjectURL(link.href); };
  return <main className="pro-page"><header className="pro-header"><a href="/">✦ VEDA/OS</a><span>ADVANCED TOOLKIT / LOCAL MATH</span><div className="pro-header-actions"><button className="pro-theme-toggle" type="button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label="Toggle colour theme">{theme === "dark" ? "☀ Light" : "☾ Dark"}</button><a className="pro-view-link" href="/advanced">Classic view →</a></div></header><section className="pro-hero"><p>YOUR PRIVATE ASTROLOGY LAB</p><h1>Go deeper than<br/><em>a birth chart.</em></h1><span>Traceable calculations for timing, chart structure and relationship comparisons.</span></section>
    <form ref={form} className="pro-console" onSubmit={(e: FormEvent) => { e.preventDefault(); run("dasha"); }}><div className="pro-profile"><label>Birth time<input name="birth_datetime" required type="datetime-local" defaultValue="1995-08-15T10:30"/></label><label>Latitude<input name="latitude" required type="number" step="any" defaultValue="28.6139"/></label><label>Longitude<input name="longitude" required type="number" step="any" defaultValue="77.2090"/></label><label>Time zone<input name="timezone" required defaultValue="Asia/Kolkata"/></label></div><div className="pro-tools">{tools.map(([kind, title, description], index) => <button key={kind} type="button" onClick={() => run(kind)}><b>0{index + 1}</b><strong>{title}</strong><span>{description}</span><i>Run →</i></button>)}</div><div className="pro-extras"><label>Prashna question<input name="question" placeholder="Ask your question for the current moment"/></label><label>Muhurat event<select name="event" defaultValue="marriage"><option value="marriage">Marriage</option><option value="business">Business</option><option value="travel">Travel</option><option value="naming">Naming</option><option value="property_purchase">Property purchase</option></select></label><label>Partner birth time<input name="match_birth_datetime" type="datetime-local" defaultValue="1996-05-04T08:15"/></label><label>Partner latitude<input name="match_latitude" type="number" step="any" defaultValue="28.6139"/></label><label>Partner longitude<input name="match_longitude" type="number" step="any" defaultValue="77.2090"/></label><label>Partner time zone<input name="match_timezone" defaultValue="Asia/Kolkata"/></label><button type="button" className="pdf-button" onClick={pdf}>Download factual PDF ↓</button></div></form>
    <section className="pro-result"><div><p>OUTPUT / {active.toUpperCase()}</p><h2>{loading ? "Calculating local chart data..." : active === "welcome" ? "Choose an advanced tool." : active.replace("_", " ")}</h2><span>No AI inference or guaranteed outcomes.</span></div>{error ? <p className="pro-error">{error}</p> : result ? <ResultBoundary key={active}><Result result={result} active={active}/></ResultBoundary> : <p className="pro-empty">Select a tool above. Each result keeps its own rules and assumptions visible.</p>}</section></main>;
}

class ResultBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <p className="pro-error">This result could not be rendered. Please run the tool again.</p> : this.props.children; }
}

function Result({ result, active }: { result: Data; active: string }) {
  if (active === "gochar") { const sade = record(result.sade_sati); const planets = records(result.planets); return <div className="pro-gochar"><article><b>{text(sade.phase)}</b><span>Sade Sati status - natal Moon {text(sade.natal_moon_sign)}, transit Saturn {text(sade.transit_saturn_sign)}</span></article>{planets.map((planet, index) => <p key={`${text(planet.name, "planet")}-${index}`}><b>{text(planet.name)}</b><span>{text(planet.sign)} / house {text(planet.house_from_lagna)}</span><i>{planet.retrograde === true ? "retrograde" : "direct"}</i></p>)}</div>; }
  if (active === "strengths") { const rows = records(result.shadbala_components); const sarva = record(result.sarvashtakavarga); const houses = records(sarva.houses_from_lagna); return <><div className="pro-strengths">{rows.map((row, index) => { const components = record(row.components); return <article key={`${text(row.planet, "planet")}-${index}`}><b>{text(row.planet)}</b><strong>{text(row.component_score)}</strong><span>Uchcha {text(components.uchcha_bala)} / Dig {text(components.dig_bala)}</span></article>; })}</div><div className="ashta-strip"><b>Sarvashtakavarga</b><span>{houses.map((house, index) => <i key={`${text(house.house)}-${index}`}>H{text(house.house)}: {text(house.bindus)}</i>)}</span><strong>Total {text(sarva.total)}</strong></div></>; }
  if (active === "prashna") { const lagna = record(result.lagna); const moon = record(result.moon); const panchang = record(result.panchang); return <div className="pro-facts"><article><b>Lagna</b><strong>{text(lagna.sign)}</strong><span>House {text(lagna.house)}</span></article><article><b>Moon</b><strong>{text(moon.sign)}</strong><span>{text(moon.nakshatra)}</span></article><article><b>Moment Nakshatra</b><strong>{text(panchang.nakshatra)}</strong><span>Question-time chart facts</span></article></div>; }
  return <pre className="pro-json">{JSON.stringify(result, null, 2)}</pre>;
}
