import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion, MotionConfig } from 'motion/react';
import { Activity, ArrowDownToLine, ArrowUpRight, ArrowRight, ChartNoAxesCombined, Check, ChevronDown, CircleHelp, Database, FlaskConical, Layers3, LayoutDashboard, Menu, Network, X } from 'lucide-react';
import { Area, AreaChart, Bar, CartesianGrid, Cell, ComposedChart, Legend, Line, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from 'recharts';
import { ContinuousTabs } from './components/ContinuousTabs';
import Landing from './Landing';
import ThemeSwitch from './components/ThemeSwitch';
import CorrelationMatrix from './components/CorrelationMatrix';
import AboutSection from './components/AboutSection';

const COLORS = ['var(--cluster-0, #9bbda8)', 'var(--cluster-1, #8aa9c5)', 'var(--cluster-2, #aca0bd)'];
const sections = [ ['Overview', LayoutDashboard], ['Market features', Activity], ['PCA analysis', Layers3], ['Market regimes', Network], ['Industry connections', Database], ['About RegX', CircleHelp] ];
const metrics = { Volatility: ['vol_20', '20-day daily volatility', '%'], Correlation: ['avg_correlation', '60-day average correlation', ''], Instability: ['covariance_instability', 'Covariance instability', ''] };
const fmt = (value, digits = 2) => Number(value).toLocaleString('en-US', { maximumFractionDigits: digits });
const dateLabel = date => new Date(date + 'T00:00:00').toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
const yearLabel = date => date.slice(0, 4);

function download(name, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement('a'); a.href = url; a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function Panel({ title, subtitle, children, className = '', action, id }) {
  return <motion.section id={id} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .4 }} className={`panel ${className}`}>
    <div className="panel-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action}</div>{children}
  </motion.section>;
}

function ChartTip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return <div className="chart-tip"><strong>{typeof label === 'string' && /^\d{4}-/.test(label) ? dateLabel(label) : label}</strong>{payload.map((p, i) => <div key={i}><span style={{ color: p.color }}>{p.name}</span><b>{fmt(p.value, 5)}</b></div>)}</div>;
}

function Spark({ points, dataKey }) {
  return <div className="spark" aria-hidden="true"><ResponsiveContainer width="100%" height="100%"><AreaChart data={points}><Area type="monotone" dataKey={dataKey} stroke="var(--accent)" fill="var(--accent-soft)" strokeWidth={1.5} isAnimationActive={false}/></AreaChart></ResponsiveContainer></div>;
}

function App() {
  const [isLanding, setIsLanding] = useState(() => window.location.hash !== '#dashboard');
  const [data, setData] = useState(null), [error, setError] = useState('');
  const [page, setPage] = useState('Overview'), [range, setRange] = useState('ALL'), [metric, setMetric] = useState('Volatility');
  const [theme, setTheme] = useState('light');
  const [help, setHelp] = useState(false), [mobile, setMobile] = useState(false), [industry, setIndustry] = useState('');
  useEffect(() => {
    const syncView = () => {
      const hash = window.location.hash;
      setIsLanding(hash !== '#dashboard');
      if (hash === '#dashboard' || hash === '' || hash === '#') window.scrollTo({ top: 0, behavior: 'instant' });
    };
    window.addEventListener('hashchange', syncView);
    return () => window.removeEventListener('hashchange', syncView);
  }, []);
  useEffect(() => { document.documentElement.dataset.theme = theme; document.querySelector('meta[name="theme-color"]')?.setAttribute('content', theme === 'light' ? '#f1eef4' : '#090c0a'); }, [theme]);
  useEffect(() => {
    if (!mobile) return;
    const close = event => { if (event.key === 'Escape') { setMobile(false); document.querySelector('.workspace-menu-toggle')?.focus(); } };
    document.addEventListener('keydown', close);
    return () => document.removeEventListener('keydown', close);
  }, [mobile]);
  useEffect(() => { const controller = new AbortController(); fetch('/data/dashboard.json', { signal: controller.signal }).then(r => { if (!r.ok) throw Error('Snapshot unavailable. Run python export_dashboard.py in RegX.'); return r.json(); }).then(setData).catch(e => { if (e.name !== 'AbortError') setError(e.message); }); return () => controller.abort(); }, []);
  useEffect(() => {
    if (!help) return;
    const previousFocus = document.activeElement;
    const listener = e => {
      if (e.key === 'Escape') setHelp(false);
      if (e.key === 'Tab') {
        const nodes = document.querySelectorAll('.method-modal button, .method-modal a');
        const first = nodes[0], last = nodes[nodes.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
      }
    };
    document.addEventListener('keydown', listener);
    return () => { document.removeEventListener('keydown', listener); previousFocus?.focus(); };
  }, [help]);
  const points = useMemo(() => {
    if (!data) return [];
    if (range === 'ALL') return data.series;
    const cutoff = new Date(data.endDate); cutoff.setFullYear(cutoff.getFullYear() - Number(range.replace('Y', '')));
    return data.series.filter(p => new Date(p.date) > cutoff);
  }, [data, range]);
  if (error) return <div className="loading"><Database size={36}/><h1>Snapshot unavailable</h1><p>{error}</p><button onClick={() => location.reload()}>Try again</button></div>;
  if (!data) return <div className="loading"><Activity className="loading-mark" size={40}/><p>Opening your market workspace…</p></div>;
  const latest = data.series.at(-1), clusterTotal = data.clusters.reduce((sum, c) => sum + c.count, 0);
  const overview = page === 'Overview', [metricKey, metricName, unit] = metrics[metric];
  const industries = data.industries.filter(name => name.toLowerCase().includes(industry.toLowerCase()));
  const descriptions = { Overview: 'A clearer perspective on a century of market behavior.', 'Market features': 'Explore the signals behind changing market structure.', 'PCA analysis': 'Understand the common forces moving 30 industries.', 'Market regimes': 'Discover recurring patterns across market history.', 'Industry connections': 'Explore how industry returns move together, one pair at a time.', 'About RegX': 'The project, the research, and the ideas behind the analysis.' };
  const exportCsv = () => { const keys = ['date', 'vol_20', 'vol_252', 'avg_correlation', 'covariance_instability', 'cluster']; download('regx-market-features.csv', keys.join(',') + '\n' + points.map(p => keys.map(k => p[k]).join(',')).join('\n'), 'text/csv'); };

  const openDashboard = () => { window.location.hash = 'dashboard'; setIsLanding(false); window.scrollTo({ top: 0, behavior: 'instant' }); };
  const navigate = name => { setPage(name); setMobile(false); window.scrollTo({ top: 0, behavior: 'instant' }); };
  if (isLanding) return <MotionConfig reducedMotion="user"><Landing data={data} theme={theme} onTheme={setTheme} onEnter={openDashboard}/></MotionConfig>;
  return <MotionConfig reducedMotion="user"><div className="app-shell">
    <div className="main-shell"><header className="dashboard-header"><div className="dashboard-header-inner">
      <a className="brand" href="#" aria-label="RegX home" onClick={() => { setIsLanding(true); window.scrollTo({ top: 0, behavior: 'instant' }); }}><span className="brand-icon"><ChartNoAxesCombined size={25}/></span>Reg<span className="brand-x">X</span><span className="brand-label">RESEARCH</span></a>
      <button className="workspace-menu-toggle" onClick={() => setMobile(!mobile)} aria-expanded={mobile} aria-controls="workspace-navigation"><Menu size={18}/><span>{page}</span><ChevronDown size={16} className={mobile ? 'rotated' : ''}/></button>
      <div className="dashboard-header-actions"><button className="methodology-button" onClick={() => setHelp(true)}><CircleHelp size={18}/><span>Methodology</span></button><ThemeSwitch value={theme} onChange={setTheme}/></div>
      </div><AnimatePresence>{mobile && <motion.nav id="workspace-navigation" className="workspace-navigation" aria-label="Workspace sections" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: .24, ease: [.2, .7, .2, 1] }}><div>{sections.map(([name, Icon], index) => <button key={name} onClick={() => navigate(name)} className={page === name ? 'active' : ''} aria-current={page === name ? 'page' : undefined}><Icon size={22}/><span>{name}</span><small>0{index + 1}</small><ArrowUpRight size={16}/></button>)}</div></motion.nav>}</AnimatePresence></header>
    <main><div className="page-heading"><div><div className="eyebrow"><span/>THE MARKET, IN CONTEXT</div><h1>{overview ? 'Market overview' : page}</h1><p>{descriptions[page]}</p></div>{page !== 'About RegX' && <button className="export-button" onClick={exportCsv}><ArrowDownToLine size={16}/>Export data</button>}</div>
    <div className="data-strip"><span><Database size={14}/>30 Industry Portfolios</span><span className="strip-divider"/><span>{dateLabel(data.startDate)} — {dateLabel(data.endDate)}</span><span className="verified"><Check size={13}/>Validated dataset</span></div>
    {overview && <div className="stat-grid">
      {[['Observations', fmt(data.observations, 0), 'Daily returns · full dataset', Database, 'market_return'], ['Industries', '30', 'Diversified industry portfolios', Layers3, 'avg_correlation'], ['Years of history', String(new Date(data.endDate).getFullYear() - new Date(data.startDate).getFullYear()), '1926 — 2026', Activity, 'vol_20'], ['Market regimes', '03', `${fmt(clusterTotal, 0)} classified observations`, Network, 'covariance_instability']].map(([label, value, note, Icon, key], i) => <motion.article className="stat-card" key={label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * .06 }}><div className="stat-label">{label}<Icon size={16}/></div><div className="stat-value">{value}{i === 2 && <span>yrs</span>}</div><div className="stat-note">{note}</div><Spark points={data.series.slice(-45)} dataKey={key}/></motion.article>)}
    </div>}
    {page === 'Market features' && <Panel title="Market pulse" subtitle="How market structure evolves over time" className="pulse-panel" action={<ContinuousTabs label="Chart date range" options={['1Y', '5Y', '10Y', 'ALL']} value={range} onChange={setRange}/> }>
      <div className="pulse-toolbar"><div className="metric-selector">{Object.keys(metrics).map(name => <button className={metric === name ? 'active' : ''} key={name} onClick={() => setMetric(name)}>{name}</button>)}</div><span className="chart-frequency"><span/>MONTH-END SNAPSHOTS</span></div>
      <div className="chart-metric"><strong>{fmt(latest[metricKey], metricKey === 'covariance_instability' ? 5 : 2)}<span>{unit}</span></strong><div>{metricName}<small>As of {dateLabel(latest.date)}</small></div></div>
      <div className="main-chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={points} margin={{ top: 10, right: 8, left: -20, bottom: 0 }}><defs><linearGradient id="pulseFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--accent)" stopOpacity={.24}/><stop offset="95%" stopColor="var(--accent)" stopOpacity={0}/></linearGradient></defs><CartesianGrid vertical={false} stroke="var(--grid)" strokeDasharray="3 5"/><XAxis dataKey="date" tickFormatter={range === '1Y' ? dateLabel : yearLabel} minTickGap={60} axisLine={false} tickLine={false} tick={{ fill: 'var(--muted)', fontSize: 11 }}/><YAxis tickFormatter={v => fmt(v, 3) + unit} axisLine={false} tickLine={false} tick={{ fill: 'var(--muted)', fontSize: 11 }}/><Tooltip content={<ChartTip/>}/><Area key={metricKey} type="monotone" dataKey={metricKey} name={metricName} stroke="var(--accent)" fill="url(#pulseFill)" strokeWidth={1.6} animationDuration={650}/></AreaChart></ResponsiveContainer></div>
      <div className="chart-footer"><span><i className="legend-line"/>{metricName}</span><span>{fmt(points.length, 0)} monthly points <span className="dot-separator">·</span> Calculated from daily returns</span></div>
    </Panel>}
    <div className={overview ? 'analysis-grid' : 'detail-grid'}>
    {(overview || page === 'PCA analysis') && <Panel title="The common market factor" subtitle="Principal component analysis" action={<span className="tag">PCA</span>}>
      <div className="pca-hero"><div><span className="micro-label">PC1 EXPLAINED VARIANCE</span><strong>{data.pca[0].variance.toFixed(2)}<span>%</span></strong></div><div className="pca-orbit"><Layers3 size={27}/></div></div><p className="insight">One common factor explains most of the shared movement across industries.</p>
      <div className="pca-chart"><ResponsiveContainer width="100%" height="100%"><ComposedChart data={data.pca} margin={{ left: -25, right: 4, top: 12, bottom: 0 }}><CartesianGrid vertical={false} stroke="var(--grid)"/><XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--muted)', fontSize: 10 }}/><YAxis domain={[0, 100]} tickFormatter={v => v + '%'} axisLine={false} tickLine={false} tick={{ fill: 'var(--muted)', fontSize: 10 }}/><Tooltip content={<ChartTip/>}/><Bar dataKey="variance" name="Explained variance (%)" radius={[4, 4, 0, 0]} barSize={30}>{data.pca.map((_, i) => <Cell key={i} fill={i === 0 ? 'var(--accent)' : 'var(--bar)'}/>)}</Bar><Line type="monotone" dataKey="cumulative" name="Cumulative (%)" stroke="var(--secondary)" strokeWidth={1.5} dot={{ r: 3 }}/></ComposedChart></ResponsiveContainer></div>
      <div className="panel-summary"><span>First 5 principal components</span><strong>{data.pca.at(-1).cumulative.toFixed(2)}% <ArrowUpRight size={14}/></strong></div>
    </Panel>}
    {(overview || page === 'Market regimes') && <Panel title="A spectrum of market states" subtitle="K-means regime distribution" action={<span className="tag">3 CLUSTERS</span>}>
      <div className="regime-viz"><svg viewBox="0 0 160 160" role="img" aria-label="Distribution of classified daily observations"><circle cx="80" cy="80" r="62" fill="none" stroke="var(--grid)" strokeWidth="15"/>{data.clusters.map((c, i) => { const start = data.clusters.slice(0, i).reduce((s, v) => s + v.count, 0) / clusterTotal; const share = c.count / clusterTotal; return <motion.circle key={c.id} cx="80" cy="80" r="62" fill="none" stroke={COLORS[i]} strokeWidth="15" pathLength="100" strokeDasharray={`${share * 100 - 1.3} ${100 - share * 100 + 1.3}`} strokeDashoffset={-start * 100} transform="rotate(-90 80 80)" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: .15 * i }}/>; })}<text x="80" y="77" textAnchor="middle" className="donut-value">{fmt(clusterTotal, 0)}</text><text x="80" y="96" textAnchor="middle" className="donut-caption">classified days</text></svg><div className="regime-legend">{data.clusters.map((c, i) => <div key={c.id}><span className="regime-dot" style={{ background: COLORS[i] }}/><div>Cluster {c.id}<small>{(100 * c.count / clusterTotal).toFixed(1)}% of classified days</small></div><strong>{fmt(c.count, 0)}</strong></div>)}</div></div>
      <div className="regime-bar">{data.clusters.map((c, i) => <div key={i} style={{ flex: c.count, background: COLORS[i] }}/>)}</div><p className="fine-print">{fmt(data.warmupRows, 0)} initial rows excluded for rolling-window warm-up. Cluster numbers are identifiers, not risk rankings.</p><button className="text-action" onClick={() => overview ? setPage('Market regimes') : setHelp(true)}>Explore regime methodology <ArrowRight size={15}/></button>
    </Panel>}
    </div>
    {page === 'PCA analysis' && <Panel title="Industry returns in two dimensions" subtitle="Every 20th classified day · PCA fitted on the full historical dataset"><div className="scatter-chart"><ResponsiveContainer width="100%" height="100%"><ScatterChart margin={{ top: 20, right: 25, left: 5, bottom: 20 }}><CartesianGrid stroke="var(--grid)"/><XAxis type="number" dataKey="x" name="PC1" tick={{ fill: 'var(--muted)' }} label={{ value: 'PC1 score', position: 'insideBottom', offset: -14, fill: 'var(--muted)' }}/><YAxis type="number" dataKey="y" name="PC2" tick={{ fill: 'var(--muted)' }}/><Tooltip cursor={{ strokeDasharray: '3 3' }}/><Legend/>{data.clusters.map((c, i) => <Scatter key={c.id} name={`Cluster ${c.id}`} data={data.scatter.filter(p => p.cluster === c.id)} fill={COLORS[i]} fillOpacity={.65}/>)}</ScatterChart></ResponsiveContainer></div></Panel>}
    {page === 'Market regimes' && <Panel title="Regime characteristics" subtitle="Historical cluster averages · descriptive analysis"><div className="table-scroll"><table><thead><tr><th>Regime</th><th>Classified days</th><th>20-day volatility</th><th>Correlation</th><th>Covariance instability</th></tr></thead><tbody>{data.clusters.map((c, i) => <tr key={c.id}><td><i className="regime-dot" style={{ background: COLORS[i] }}/>Cluster {c.id}</td><td>{fmt(c.count, 0)}</td><td>{fmt(c.summary.vol_20 * 100, 3)}%</td><td>{fmt(c.summary.avg_correlation, 3)}</td><td>{fmt(c.summary.covariance_instability, 5)}</td></tr>)}</tbody></table></div><div className="method-note"><CircleHelp size={16}/><p>Standardized features and PC1–PC3 feed K-means (k=3, seed=42). Full-sample fitting describes historical states; it does not validate out-of-sample predictions.</p></div></Panel>}
    {page === 'Industry connections' && <Panel title="Industry connections" subtitle="Full-history pairwise return correlations · hover or tap to inspect" className="connections-panel" action={<span className="tag">30 × 30</span>}><CorrelationMatrix data={data}/></Panel>}
    {page === 'Industry connections' && <Panel title="Industry universe" subtitle="Original Kenneth French portfolio labels" action={<input className="search" placeholder="Find an industry…" aria-label="Find an industry" value={industry} onChange={e => setIndustry(e.target.value)}/>}><div className="industry-list">{industries.length ? industries.map(name => <span key={name}>{name}</span>) : <p>No matching industries.</p>}</div></Panel>}
    {overview && <div className="overview-links"><button onClick={() => navigate('Market features')}><Activity size={24}/><div><strong>Follow the market pulse</strong><span>Explore volatility, correlation, and structural instability.</span></div><ArrowUpRight size={21}/></button><button onClick={() => navigate('Industry connections')}><Database size={24}/><div><strong>Explore industry connections</strong><span>Inspect the full, labeled correlation matrix.</span></div><ArrowUpRight size={21}/></button></div>}
    {page === 'About RegX' && <AboutSection/>}
    <div className="research-note"><div className="research-icon"><FlaskConical size={19}/></div><div><strong>Built for research. Grounded in data.</strong><p>Daily industry returns from the Kenneth French Data Library. All visualizations reflect a fixed historical snapshot.</p></div><button onClick={() => setHelp(true)} aria-label="Read research methodology"><ArrowUpRight size={20}/></button></div>
    <footer><span>RegX <span className="footer-dot">/</span> Regime-aware portfolio risk research</span><span>Data through {dateLabel(data.endDate)}<span className="footer-dot">·</span><a href="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html" target="_blank" rel="noreferrer">Data source <ArrowUpRight size={11}/></a></span></footer>
    </main></div>
    <AnimatePresence>{help && <motion.div className="modal-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setHelp(false)}><motion.section role="dialog" aria-modal="true" aria-labelledby="method-title" className="method-modal" initial={{ y: 20 }} animate={{ y: 0 }} onClick={e => e.stopPropagation()}><button autoFocus className="modal-close icon-button" aria-label="Close methodology" onClick={() => setHelp(false)}><X size={20}/></button><div className="eyebrow">RESEARCH NOTES</div><h2 id="method-title">Behind the numbers.</h2><p>The website reads a generated JSON snapshot from the existing RegX Python pipeline. Regenerate it with <code>python export_dashboard.py</code>.</p><h3>Market features</h3><p>Volatility is the daily standard deviation of equal-weight market returns over 20 and 252 trading days, displayed in percent. Correlation is the average of off-diagonal industry correlations over 60 days. Instability is the Frobenius norm of the difference between 60-day and 252-day covariance matrices.</p><h3>PCA & market states</h3><p>Industry returns are standardized before PCA. K-means groups standardized market features and the first three PCA scores into three states. The PCA panel reports five components. Both models fit the full historical dataset. Initial rolling-window rows are excluded. Chart points show the last available observation of each month.</p><h3>Scope</h3><p>This dashboard presents descriptive research, not live signals. Portfolio optimization and backtesting remain in the Python project; uncomputed performance results are not displayed.</p><button className="export-button" onClick={() => download('regx-snapshot.json', JSON.stringify(data, null, 2), 'application/json')}><ArrowDownToLine size={16}/>Download full snapshot</button></motion.section></motion.div>}</AnimatePresence>
  </div></MotionConfig>;
}
export default App;
