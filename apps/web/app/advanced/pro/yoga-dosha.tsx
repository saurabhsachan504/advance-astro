"use client";

type Data = Record<string, unknown>;

const records = (value: unknown): Data[] => Array.isArray(value) ? value.filter((item): item is Data => item !== null && typeof item === "object" && !Array.isArray(item)) : [];
const text = (value: unknown, fallback = "—"): string => typeof value === "string" || typeof value === "number" ? String(value) : fallback;

function RuleList({ title, subtitle, rows, kind }: { title: string; subtitle: string; rows: Data[]; kind: "yoga" | "dosha" }) {
  return <section className={`yoga-dosha-column ${kind}`}>
    <header><div><b>{title}</b><span>{subtitle}</span></div><strong>{rows.length}</strong></header>
    {rows.length ? rows.map((row, index) => <article key={`${text(row.name)}-${index}`}>
      <div><b>{text(row.name)}</b><i className={text(row.status).toLowerCase().replace(/\s+/g, "-")}>{text(row.status)}</i></div>
      <p>{text(row.rule)}</p>
    </article>) : <p className="yoga-dosha-empty">No configured yoga was detected in this compact rule set.</p>}
  </section>;
}

export default function YogaDosha({ result }: { result: Data }) {
  const yogas = records(result.yogas);
  const doshas = records(result.doshas);
  const chartBasis = result.chart_basis !== null && typeof result.chart_basis === "object" ? result.chart_basis as Data : {};
  return <div className="yoga-dosha-studio">
    <div className="studio-intro"><div><b>Yoga & Dosha Analyzer</b><span>Classical screening rules for the selected Lahiri sidereal birth chart</span></div><small>Ascendant {text(chartBasis.ascendant_longitude)}° · {text(chartBasis.ayanamsa)}</small></div>
    <div className="yoga-dosha-grid">
      <RuleList title="Yoga signals" subtitle="Configured supportive combinations" rows={yogas} kind="yoga" />
      <RuleList title="Dosha screening" subtitle="Flags shown with their exact rule" rows={doshas} kind="dosha" />
    </div>
    <p className="astro-map-note">{text(result.notice)}</p>
  </div>;
}
