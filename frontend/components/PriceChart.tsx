"use client";
import { useEffect, useRef } from "react";
import { createChart, LineStyle, type IChartApi, type UTCTimestamp } from "lightweight-charts";

type Candle = { time: number; open: number; high: number; low: number; close: number };
type Levels = { call_wall?: number | null; put_wall?: number | null; gamma_flip?: number | null };

export default function PriceChart({ candles, levels }: { candles: Candle[]; levels?: Levels }) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const chart = createChart(ref.current, {
      height: 480,
      layout: { background: { color: "#0B0E11" }, textColor: "#E6EAF0" },
      grid: { vertLines: { color: "#1a212b" }, horzLines: { color: "#1a212b" } },
      rightPriceScale: { borderColor: "#222A33" },
      timeScale: { borderColor: "#222A33", timeVisible: true },
    });
    chartRef.current = chart;
    const series = chart.addCandlestickSeries({
      upColor: "#16C784", downColor: "#EA3943", borderVisible: false,
      wickUpColor: "#16C784", wickDownColor: "#EA3943",
    });

    series.setData(candles.map((c) => ({ ...c, time: c.time as UTCTimestamp })));

    const line = (price: number | null | undefined, color: string, title: string) => {
      if (typeof price === "number")
        series.createPriceLine({ price, color, lineWidth: 1, lineStyle: LineStyle.Dashed,
                                 axisLabelVisible: true, title });
    };
    line(levels?.call_wall, "#EA3943", "Call Wall");
    line(levels?.gamma_flip, "#3B82F6", "Zero Gamma");
    line(levels?.put_wall, "#16C784", "Put Wall");
    chart.timeScale().fitContent();

    const onResize = () => chart.applyOptions({ width: ref.current!.clientWidth });
    onResize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [candles, levels]);

  return <div ref={ref} className="w-full" />;
}
