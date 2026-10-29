import { useEffect, useRef } from 'react';
import { useReducedMotion } from 'motion/react';

export default function MarketChartBackdrop({ data, progress, theme }) {
  const ref = useRef(null);
  const reduced = useReducedMotion();
  useEffect(() => {
    const canvas = ref.current, ctx = canvas.getContext('2d');
    const points = data.marketChart || [];
    if (!ctx || points.length < 2) return;
    let width = 0, height = 0, raf, last = 0, visible = true, started;
    const observer = new ResizeObserver(([entry]) => {
      width = entry.contentRect.width; height = entry.contentRect.height;
      const ratio = Math.min(devicePixelRatio || 1, 1.5);
      canvas.width = width * ratio; canvas.height = height * ratio;
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    });
    observer.observe(canvas);
    const visibility = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; });
    visibility.observe(canvas);
    let accent, secondary, muted, grid;
    const regimes = new Map(data.series.map(row => [row.date, row.cluster]));
    const low = Math.min(...points.map(p => p.low)) * .96;
    const high = Math.max(...points.map(p => p.high)) * 1.04;
    const draw = now => {
      raf = requestAnimationFrame(draw);
      if (!visible || !width || now - last < (reduced ? 200 : 32)) return;
      if (!accent) {
        const styles = getComputedStyle(document.documentElement);
        accent = styles.getPropertyValue('--accent').trim();
        secondary = styles.getPropertyValue('--secondary').trim();
        muted = styles.getPropertyValue('--muted').trim();
        grid = styles.getPropertyValue('--grid').trim();
      }
      started ??= now; last = now;
      const phase = reduced ? 1 : progress?.get() || 0;
      const reveal = reduced ? 1 : progress ? .35 + phase * .65 : Math.min(1, (now - started) / 2200);
      const count = Math.max(2, Math.floor(points.length * reveal));
      const left = width * .08, right = width * .91, top = height * .23, bottom = height * .76;
      const x = i => left + i / (points.length - 1) * (right - left);
      const y = value => bottom - (value - low) / (high - low) * (bottom - top);
      ctx.clearRect(0, 0, width, height);
      ctx.font = '11px "DM Mono", monospace';
      for (let line = 0; line < 5; line++) {
        const yy = top + line / 4 * (bottom - top);
        ctx.globalAlpha = .5; ctx.strokeStyle = grid; ctx.lineWidth = 1;
        ctx.setLineDash([2, 7]); ctx.beginPath(); ctx.moveTo(left, yy); ctx.lineTo(right, yy); ctx.stroke(); ctx.setLineDash([]);
        ctx.globalAlpha = .6; ctx.fillStyle = muted; ctx.fillText((high - line / 4 * (high - low)).toFixed(0), right + 12, yy + 4);
      }
      // In the final chapter, bands identify real monthly regime assignments.
      if (phase > .57 && progress) {
        points.forEach((point, i) => {
          const regime = regimes.get(point.date) ?? 0;
          ctx.globalAlpha = (phase - .57) * .1;
          ctx.fillStyle = regime === 0 ? accent : regime === 1 ? secondary : muted;
          ctx.fillRect(x(i), top, (right - left) / points.length, bottom - top);
        });
      }
      const candleWidth = Math.max(3, (right - left) / points.length * .4);
      for (let i = 0; i < count; i++) {
        const point = points[i];
        ctx.globalAlpha = progress ? .5 - Math.sin(phase * Math.PI) * .2 : .42;
        ctx.strokeStyle = point.close >= point.open ? accent : secondary;
        ctx.fillStyle = ctx.strokeStyle; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(x(i), y(point.high)); ctx.lineTo(x(i), y(point.low)); ctx.stroke();
        ctx.fillRect(x(i) - candleWidth / 2, Math.min(y(point.open), y(point.close)), candleWidth, Math.max(2, Math.abs(y(point.close) - y(point.open))));
      }
      const gradient = ctx.createLinearGradient(0, top, 0, bottom);
      gradient.addColorStop(0, accent); gradient.addColorStop(1, 'transparent');
      ctx.beginPath(); ctx.moveTo(x(0), bottom);
      for (let i = 0; i < count; i++) ctx.lineTo(x(i), y(points[i].close));
      ctx.lineTo(x(count - 1), bottom); ctx.closePath();
      ctx.globalAlpha = .08; ctx.fillStyle = gradient; ctx.fill();
      ctx.beginPath(); points.slice(0, count).forEach((point, i) => i ? ctx.lineTo(x(i), y(point.close)) : ctx.moveTo(x(i), y(point.close)));
      ctx.globalAlpha = .8; ctx.strokeStyle = accent; ctx.lineWidth = 1.8; ctx.stroke();
      const cursor = reduced ? count - 1 : Math.floor(((Math.sin(now * .00016) + 1) / 2) * (count - 1));
      ctx.globalAlpha = .18; ctx.setLineDash([3, 6]); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(x(cursor), top); ctx.lineTo(x(cursor), bottom); ctx.stroke(); ctx.setLineDash([]);
      ctx.globalAlpha = 1; ctx.beginPath(); ctx.arc(x(cursor), y(points[cursor].close), 3, 0, Math.PI * 2); ctx.fillStyle = accent; ctx.fill();
      ctx.globalAlpha = .65; ctx.fillStyle = muted;
      ctx.fillText('EQUAL-WEIGHT INDUSTRY RETURN INDEX', left, top - 28);
      ctx.font = '10px "DM Mono", monospace';
      ctx.fillText('MONTHLY RANGE · BASE 100 · HISTORICAL', left, bottom + 45);
      [0, .25, .5, .75, 1].forEach(fraction => { const i = Math.floor(fraction * (points.length - 1)); ctx.fillText(points[i].date.slice(0, 7), x(i) - 15, bottom + 23); });
      ctx.globalAlpha = 1;
    };
    raf = requestAnimationFrame(draw);
    return () => { cancelAnimationFrame(raf); observer.disconnect(); visibility.disconnect(); };
  }, [data, progress, theme, reduced]);
  return <canvas ref={ref} className="market-surface stock-field" aria-hidden="true"/>;
}
