"use client";
// Plotly is client-only and heavy; this component is dynamic-imported with
// ssr:false from the page. Builds a strike x DTE x IV surface from the chain.
import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "plotly.js-dist-min";

const Plot = createPlotlyComponent(Plotly as any);

type Row = { strike: number; dte: number; iv: number };

export default function VolSurface({ rows }: { rows: Row[] }) {
  const strikes = Array.from(new Set(rows.map((r) => r.strike))).sort((a, b) => a - b);
  const dtes = Array.from(new Set(rows.map((r) => r.dte))).sort((a, b) => a - b);
  const z = dtes.map((d) =>
    strikes.map((s) => {
      const m = rows.filter((r) => r.dte === d && r.strike === s && typeof r.iv === "number");
      return m.length ? m.reduce((a, r) => a + r.iv, 0) / m.length : null;
    })
  );

  return (
    <Plot
      data={[{ type: "surface", x: strikes, y: dtes, z, colorscale: "Viridis",
               colorbar: { title: "IV %" } } as any]}
      layout={{
        autosize: true, height: 600,
        paper_bgcolor: "#0B0E11", plot_bgcolor: "#0B0E11",
        font: { color: "#E6EAF0" },
        scene: { xaxis: { title: "Strike" }, yaxis: { title: "DTE" },
                 zaxis: { title: "IV %" } },
        margin: { l: 0, r: 0, t: 10, b: 0 },
      } as any}
      style={{ width: "100%", height: "600px" }}
      config={{ displayModeBar: false, responsive: true } as any}
      useResizeHandler
    />
  );
}
