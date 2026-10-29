import { useState } from 'react';

export default function CorrelationMatrix({ data }) {
  const [pair, setPair] = useState([0, 1]);
  const [row, col] = pair;
  return <div className="correlation-view">
    <div className="matrix-summary"><div><span>SELECTED INDUSTRY PAIR</span><strong>{data.industries[row]} <i>×</i> {data.industries[col]}</strong></div><div><span>CORRELATION</span><strong>{data.correlation[row][col].toFixed(3)}</strong></div><p>Hover, focus, or tap a cell to inspect. Both axes use the original industry labels.</p></div>
    <div className="matrix-scroll" tabIndex={0} role="region" aria-label="Scrollable industry correlation matrix">
      <div className="labeled-matrix" role="group" aria-label="30 by 30 industry correlation matrix">
        <span className="matrix-corner"/>{data.industries.map((name, i) => <span className={`matrix-col-label ${i === col ? 'highlight' : ''}`} key={`col-${name}`}>{name}</span>)}
        {data.correlation.map((values, i) => <div className="matrix-row" key={i}><span className={`matrix-row-label ${i === row ? 'highlight' : ''}`}>{data.industries[i]}</span>{values.map((value, j) => <button key={j} className={`matrix-cell ${i === row && j === col ? 'selected' : ''}`} style={{ background: `color-mix(in srgb, var(--accent) ${Math.max(5, (value + 1) / 2 * 100)}%, var(--heat-base))` }} onMouseEnter={() => setPair([i, j])} onFocus={() => setPair([i, j])} onClick={() => setPair([i, j])} aria-label={`${data.industries[i]} / ${data.industries[j]}: ${value.toFixed(3)}`} aria-pressed={i === row && j === col}/>)}</div>)}
      </div>
    </div>
    <div className="matrix-footer"><span>Negative correlation</span><span className="matrix-scale">−1 <i/> +1</span><span>Positive correlation</span></div>
  </div>;
}
