"use client";

import { FormEvent, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "";
type Result = Record<string, unknown>;

function requestPayload(form: HTMLFormElement) {
  const data = new FormData(form);
  return { birth_datetime: data.get("birth_datetime"), timezone: data.get("timezone"), latitude: Number(data.get("latitude")), longitude: Number(data.get("longitude")), ayanamsa: "lahiri" };
}

export default function AdvancedObservatory() {
  const [result, setResult] = useState<Result | null>(null);
  const [mode, setMode] = useState("welcome");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [event, setEvent] = useState("marriage");
  const run = async (path: string, payload: Record<string, unknown>, label: string) => {
    setError(""); setLoading(true); setMode(label);
    try { const response = await fetch(`${API}/api/v1${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); const body = await response.text(); if (!response.ok) throw new Error(JSON.parse(body).detail || "Calculation unavailable"); setResult(JSON.parse(body)); } catch (reason) { setError(reason instanceof Error ? reason.message : "Calculation unavailable"); } finally { setLoading(false); }
  };
  const runProfile = (action: string) => (form: HTMLFormElement) => {
    const payload = requestPayload(form);
    if (action === "dasha") return run("/dasha/vimshottari", { ...payload, years: 20 }, "dasha");
    if (action === "kundli") return run("/kundli/interactive", { ...payload, layout: "north_indian" }, "kundli");
    const date = String(payload.birth_datetime).slice(0, 10);
    if (action === "calendar") return run("/calendar/panchang", { date, timezone: payload.timezone, latitude: payload.latitude, longitude: payload.longitude }, "calendar");
    return run("/muhurat/plan", { date, timezone: payload.timezone, latitude: payload.latitude, longitude: payload.longitude, event, end_date: date }, "muhurat");
  };
  const submitMatch = (form: HTMLFormElement) => {
    const a = requestPayload(form); const data = new FormData(form);
    const b = { birth_datetime: data.get("match_birth_datetime"), timezone: data.get("match_timezone"), latitude: Number(data.get("match_latitude")), longitude: Number(data.get("match_longitude")), ayanamsa: "lahiri" };
    return run("/matchmaking/analyse", { person_a: a, person_b: b, person_a_label: "Profile A", person_b_label: "Profile B" }, "match");
  };
  return <main className="advanced-page"><header className="advanced-header"><a href="/" className="advanced-brand"><span>✦</span> VEDA/OS</a><div><a href="/">Birth chart</a><b>Advanced observatory</b></div></header>
    <section className="advanced-hero"><p>LOCAL ASTROLOGY TOOLKIT</p><h1>Time, pattern<br/><em>&amp; compatibility.</em></h1><span>All calculations run through your private Swiss Ephemeris backend. No cloud AI is required.</span></section>
    <form className="profile-console" onSubmit={(e: FormEvent<HTMLFormElement>) => { e.preventDefault(); runProfile("dasha")(e.currentTarget); }}><div className="console-title"><div><p>YOUR REFERENCE PROFILE</p><h2>Start with birth facts.</h2></div><small>01 / deterministic math</small></div><div className="advanced-fields"><label><span>Birth date &amp; time</span><input required name="birth_datetime" type="datetime-local" defaultValue="1995-08-15T10:30"/></label><label><span>Latitude</span><input required name="latitude" type="number" step="any" defaultValue="28.6139"/></label><label><span>Longitude</span><input required name="longitude" type="number" step="any" defaultValue="77.2090"/></label><label><span>Time zone</span><input required name="timezone" defaultValue="Asia/Kolkata"/></label></div>
      <div className="tool-grid"><button type="button" onClick={(e) => runProfile("dasha")((e.currentTarget.form as HTMLFormElement))}><b>01</b><strong>Vimshottari Dasha</strong><span>Maha + Antardasha timeline</span></button><button type="button" onClick={(e) => runProfile("kundli")((e.currentTarget.form as HTMLFormElement))}><b>02</b><strong>Interactive Kundli</strong><span>D1 houses, D9 &amp; D10 divisions</span></button><button type="button" onClick={(e) => runProfile("calendar")((e.currentTarget.form as HTMLFormElement))}><b>03</b><strong>Astro calendar</strong><span>Panchang, Rahu Kaal, Choghadiya</span></button><button type="button" onClick={(e) => runProfile("muhurat")((e.currentTarget.form as HTMLFormElement))}><b>04</b><strong>Muhurat planner</strong><span>Local favourable time windows</span></button></div><div className="event-picker"><span>Muhurat event</span>{["marriage", "business", "travel", "naming", "property_purchase"].map((item) => <button key={item} type="button" className={event === item ? "selected" : ""} onClick={() => setEvent(item)}>{item.replace("_", " ")}</button>)}</div>
      <div className="match-console"><div><p>02 / PARTNER PROFILE</p><h3>Matchmaking analysis</h3></div><label><span>Birth date &amp; time</span><input required name="match_birth_datetime" type="datetime-local" defaultValue="1996-05-04T08:15"/></label><label><span>Latitude</span><input required name="match_latitude" type="number" step="any" defaultValue="28.6139"/></label><label><span>Longitude</span><input required name="match_longitude" type="number" step="any" defaultValue="77.2090"/></label><label><span>Time zone</span><input required name="match_timezone" defaultValue="Asia/Kolkata"/></label><button type="button" className="match-button" onClick={(e) => submitMatch(e.currentTarget.form as HTMLFormElement)}>Compare charts →</button></div></form>
    <section className="advanced-results"><div className="result-heading"><p>CALCULATION OUTPUT</p><h2>{loading ? "Calculating..." : mode === "welcome" ? "Choose a tool." : mode.replace("_", " ")}</h2><span>Transparent rules, not guaranteed outcomes.</span></div>{error ? <p className="advanced-error">{error}</p> : <Results mode={mode} result={result}/>}</section>
  </main>;
}

function Results({ mode, result }: { mode: string; result: Result | null }) {
  if (!result) return <div className="empty-result"><span>✦</span><p>Select any calculation above to reveal its local, traceable result.</p></div>;
  if (mode === "dasha") { const periods = result.periods as { lord: string; start: string; end: string; antardashas: { lord: string; start: string; end: string }[] }[]; return <div className="dasha-result">{periods.slice(0, 4).map((period) => <article key={period.start}><b>{period.lord} Mahadasha</b><small>{new Date(period.start).toLocaleDateString()} - {new Date(period.end).toLocaleDateString()}</small><div>{period.antardashas.map((antar) => <span key={antar.start}>{antar.lord}</span>)}</div></article>)}</div>; }
  if (mode === "kundli") { const houses = result.houses as { house: number; sign: string; occupants: string[] }[]; return <div className="house-grid">{houses.map((house) => <article key={house.house}><b>{house.house}</b><strong>{house.sign}</strong><span>{house.occupants.join(", ") || "—"}</span></article>)}</div>; }
  if (mode === "calendar") { const tithi = result.tithi as { name: string; paksha: string }; const rahu = result.rahu_kaal as { start: string; end: string }; const choghadiya = result.choghadiya as { day: { name: string; start: string; end: string; favourable: boolean }[] }; return <div className="calendar-result"><div className="calendar-facts"><b>{tithi.name}</b><span>{tithi.paksha} Paksha</span><span>Rahu: {new Date(rahu.start).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} - {new Date(rahu.end).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span></div><div className="time-slots">{choghadiya.day.map((slot) => <span className={slot.favourable ? "good" : ""} key={slot.start}><b>{slot.name}</b><small>{new Date(slot.start).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</small></span>)}</div></div>; }
  if (mode === "muhurat") { const windows = result.windows as { start: string; end: string; choghadiya: string; nakshatra: string }[]; return <div className="muhurat-result">{windows.length ? windows.map((window) => <article key={window.start}><b>{window.choghadiya}</b><span>{new Date(window.start).toLocaleString()} - {new Date(window.end).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span><small>{window.nakshatra}</small></article>) : <p>No baseline windows found for this date.</p>}</div>; }
  if (mode === "match") { const ashtakoota = result.ashtakoota as { score: number; maximum: number; kutas: { name: string; score: number; maximum: number }[] }; const kp = result.kp_comparison as { score: number }; return <div className="match-result"><div><b>{ashtakoota.score} / {ashtakoota.maximum}</b><span>Ashtakoota baseline</span><strong>KP comparison: {kp.score}/100</strong></div><section>{ashtakoota.kutas.map((kuta) => <p key={kuta.name}><span>{kuta.name}</span><b>{kuta.score}/{kuta.maximum}</b></p>)}</section></div>; }
  return null;
}
