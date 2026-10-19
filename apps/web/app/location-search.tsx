"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "";

type LocationResult = { label: string; latitude: number; longitude: number; timezone: string };

function setField(form: HTMLFormElement, name: string, value: string) {
  const field = form.elements.namedItem(name);
  if (!(field instanceof HTMLInputElement)) return;
  field.value = value;
  field.dispatchEvent(new Event("input", { bubbles: true }));
  field.dispatchEvent(new Event("change", { bubbles: true }));
}

export default function LocationSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<LocationResult[]>([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function search() {
    const value = query.trim();
    if (value.length < 2) { setStatus("Enter at least 2 characters."); return; }
    setLoading(true); setStatus(""); setResults([]);
    try {
      const response = await fetch(`${API}/api/v1/locations/search?query=${encodeURIComponent(value)}`);
      const body = await response.json() as { results?: LocationResult[]; detail?: string };
      if (!response.ok) throw new Error(body.detail || "Location search is unavailable.");
      const matches = body.results || [];
      setResults(matches);
      if (!matches.length) setStatus("No matching city found. Try city, state or country.");
    } catch (reason) { setStatus(reason instanceof Error ? reason.message : "Location search is unavailable."); } finally { setLoading(false); }
  }

  function applyLocation(location: LocationResult) {
    document.querySelectorAll<HTMLFormElement>("form").forEach((form) => {
      setField(form, "latitude", String(location.latitude));
      setField(form, "longitude", String(location.longitude));
      setField(form, "timezone", location.timezone);
    });
    setStatus(`${location.label} applied to this page.`);
    setResults([]);
  }

  return <aside className={`location-search${open ? " open" : ""}`} aria-label="Location search">
    {open && <div className="location-search-panel">
      <div className="location-search-title"><div><b>Birth location</b><span>City fills coordinates &amp; timezone</span></div><button type="button" onClick={() => setOpen(false)} aria-label="Close location search">×</button></div>
      <div className="location-search-input"><input value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); search(); } }} placeholder="Search city, e.g. Delhi, India" /><button type="button" onClick={search} disabled={loading}>{loading ? "Searching..." : "Search"}</button></div>
      {results.length > 0 && <div className="location-results">{results.map((location) => <button type="button" key={`${location.latitude}-${location.longitude}-${location.timezone}`} onClick={() => applyLocation(location)}><b>{location.label}</b><span>{location.latitude.toFixed(4)}, {location.longitude.toFixed(4)} · {location.timezone}</span></button>)}</div>}
      {status && <p className="location-status" role="status">{status}</p>}
      <small>Your typed city is used only for this lookup. Profiles remain in your browser.</small>
    </div>}
    <button className="location-search-trigger" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}><span aria-hidden="true">⌖</span>{open ? "Close location" : "Set location"}</button>
  </aside>;
}
