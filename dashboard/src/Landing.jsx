import { useRef, useState } from 'react';
import { AnimatePresence, motion, useMotionValueEvent, useReducedMotion, useScroll, useSpring, useTransform } from 'motion/react';
import { ArrowDown, ArrowRight, ArrowUpRight, ChartNoAxesCombined } from 'lucide-react';
import MarketChartBackdrop from './components/MarketChartBackdrop';
import ScrollResearchCard from './components/ScrollResearchCard';
import { ContinuousTabs } from './components/ContinuousTabs';
import ThemeSwitch from './components/ThemeSwitch';
import AboutSection from './components/AboutSection';
import './landing.css';

const number = value => value.toLocaleString('en-US');
const chapters = ['Market structure', 'Common factors', 'Market regimes'];

function Reveal({ children, className = '' }) {
  return <motion.div className={className} initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: .3 }} transition={{ duration: .8, ease: [.2, .7, .2, 1] }}>{children}</motion.div>;
}

function Preview({ data, onEnter }) {
  const ref = useRef(null), reduced = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'center center'] });
  const progress = useSpring(scrollYProgress, { stiffness: 95, damping: 27 });
  const rotateX = useTransform(progress, [0, 1], [17, 0]);
  const scale = useTransform(progress, [0, 1], [.88, 1]);
  const y = useTransform(progress, [0, 1], [100, 0]);
  const samples = data.series.slice(-120);
  const max = Math.max(...samples.map(p => p.vol_20));
  const path = samples.map((p, i) => `${i ? 'L' : 'M'}${i / (samples.length - 1) * 800},${165 - p.vol_20 / max * 140}`).join(' ');
  return <section className="landing-workspace" ref={ref} id="workspace-preview">
    <Reveal className="workspace-intro"><span className="landing-kicker">THE RESEARCH WORKSPACE</span><h2>Less noise.<br/><span>More perspective.</span></h2><p>Follow the signal from a century of returns<br className="desktop-break"/> to the structure underneath.</p></Reveal>
    <div className="preview-perspective"><motion.div className="workspace-preview" style={reduced ? {} : { rotateX, scale, y, transformPerspective: 1600 }}>
      <div className="preview-toolbar"><span><ChartNoAxesCombined size={17}/>RegX <i>/</i> Market intelligence</span><span className="preview-status"><i/>Historical snapshot</span></div>
      <div className="preview-body"><div className="preview-title"><div><span className="landing-kicker">A CENTURY. ONE CONNECTED VIEW.</span><h3>Market overview</h3></div><button onClick={onEnter} className="preview-open" aria-label="Open interactive dashboard"><ArrowUpRight size={22}/></button></div>
      <div className="preview-stats"><div><span>DAILY OBSERVATIONS</span><strong>{number(data.observations)}</strong></div><div><span>INDUSTRY PORTFOLIOS</span><strong>30</strong></div><div><span>PC1 EXPLAINED VARIANCE</span><strong>{data.pca[0].variance.toFixed(2)}<small>%</small></strong></div></div>
      <div className="preview-chart-heading"><span><i/>20-day market volatility</span><span>LAST 10 YEARS · MONTHLY SNAPSHOTS</span></div>
      <svg className="preview-chart" viewBox="0 0 800 190" role="img" aria-label="20-day volatility over the last ten years, sampled monthly"><defs><linearGradient id="landing-chart-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="var(--accent)" stopOpacity=".16"/><stop offset="1" stopColor="var(--accent)" stopOpacity="0"/></linearGradient></defs>{[25, 70, 115, 160].map(pos => <line key={pos} x1="0" y1={pos} x2="800" y2={pos} stroke="var(--grid)" strokeDasharray="3 5"/>)}<path d={`${path} L800,180 L0,180 Z`} fill="url(#landing-chart-fill)"/><path d={path} fill="none" stroke="var(--accent)" strokeWidth="1.8"/>{[0, 30, 60, 90, 119].map(i => <text key={i} x={i / 119 * 795} y="189" textAnchor={i === 119 ? 'end' : 'start'} fill="var(--muted)" fontSize="9" fontFamily="monospace">{samples[i].date.slice(0, 4)}</text>)}</svg>
      <div className="preview-foot"><span>Daily returns. Validated. Connected.</span><button onClick={onEnter}>Explore the full dashboard <ArrowRight size={15}/></button></div></div>
    </motion.div></div>
  </section>;
}

export default function Landing({ data, theme, onTheme, onEnter }) {
  const storyRef = useRef(null), heroRef = useRef(null), reduced = useReducedMotion();
  const [chapter, setChapter] = useState(0);
  const { scrollYProgress } = useScroll({ target: storyRef, offset: ['start start', 'end end'] });
  const progress = useSpring(scrollYProgress, { stiffness: 85, damping: 28, restDelta: .0001 });
  const { scrollYProgress: heroProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] });
  const heroY = useTransform(heroProgress, [0, 1], [0, 150]);
  const heroOpacity = useTransform(heroProgress, [0, .7], [1, 0]);
  const surfaceScale = useTransform(progress, [0, .35, .7, 1], [.94, 1.08, .98, 1.06]);
  useMotionValueEvent(progress, 'change', value => setChapter(Math.min(2, Math.floor(value * 3))));
  const goTo = id => document.getElementById(id)?.scrollIntoView({ behavior: reduced ? 'instant' : 'smooth' });
  const selectChapter = name => { const index = chapters.indexOf(name); const el = storyRef.current; const top = el.getBoundingClientRect().top + window.scrollY; window.scrollTo({ top: top + (el.offsetHeight - window.innerHeight) * [.12, .48, .87][index], behavior: reduced ? 'instant' : 'smooth' }); };
  const clusterTotal = data.clusters.reduce((sum, c) => sum + c.count, 0);
  const recentVolatility = data.series.slice(-22);
  const maxRecentVolatility = Math.max(...recentVolatility.map(point => point.vol_20));
  return <div className="landing">
    <a className="landing-skip" href="#research-story">Skip to research</a>
    <header className="landing-nav"><a className="landing-brand" href="#" onClick={e => { e.preventDefault(); window.scrollTo({ top: 0, behavior: reduced ? 'instant' : 'smooth' }); }}><ChartNoAxesCombined size={24}/>Reg<span>X</span><small>RESEARCH</small></a><nav aria-label="Landing navigation"><button onClick={() => goTo('research-story')}>The approach</button><button onClick={() => goTo('workspace-preview')}>The workspace</button><button onClick={() => goTo('about-regx')}>About</button></nav><div><ThemeSwitch value={theme} onChange={onTheme}/></div></header>
    <section className="landing-hero" ref={heroRef}>
      <div className="hero-grid" aria-hidden="true"/><div className="hero-visual"><MarketChartBackdrop data={data} theme={theme}/></div>
      <motion.div className="hero-content" style={reduced ? {} : { y: heroY, opacity: heroOpacity }}>
        <motion.span className="landing-kicker" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: .8 }}>REGIME-AWARE MARKET RESEARCH</motion.span>
        <h1><span className="headline-mask"><motion.span initial={{ y: '110%' }} animate={{ y: 0 }} transition={{ duration: 1, ease: [.16, 1, .3, 1] }}>See beyond</motion.span></span><span className="headline-mask"><motion.span className="headline-muted" initial={{ y: '110%' }} animate={{ y: 0 }} transition={{ duration: 1, delay: .13, ease: [.16, 1, .3, 1] }}>the market.</motion.span></span></h1>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .4, duration: .8 }}><p>A century of returns. A deeper view of risk.<br/>Explore the patterns that connect markets,<br className="desktop-break"/> industries, and changing regimes.</p><div className="hero-actions"><button className="landing-primary explore-primary" onClick={() => goTo('research-story')}>Scroll to explore <ArrowDown size={19}/></button></div><p className="explore-caption">Three perspectives. One connected story.</p></motion.div>
      </motion.div>
      <div className="hero-bottom"><button onClick={() => goTo('research-story')} className="scroll-cue"><span className="scroll-cue-line"/>SCROLL TO EXPLORE</button><span>1926 — 2026 <i/>30 INDUSTRIES <i/>26,317 OBSERVATIONS</span><span className="hero-edition">RESEARCH EDITION / 01</span></div>
    </section>
    <section className="landing-statement"><Reveal><span className="landing-kicker">MARKETS ARE COMPLEX. YOUR PERSPECTIVE SHOULDN’T BE.</span><h2>Behind every movement,<br/>there is <span>a structure.</span></h2></Reveal><Reveal className="statement-aside"><span>01 / THE APPROACH</span><p>RegX brings volatility, correlation, and market regimes into one research framework. Start with the data. Find the common factors. Understand what changes.</p></Reveal></section>
    <section ref={storyRef} id="research-story" className={`research-scroll ${reduced ? 'motion-reduced' : ''}`} aria-label="Scroll through the RegX research approach">
      <div className="research-sticky"><div className="story-topline"><span className="landing-kicker">FROM MOVEMENT TO MEANING</span><span>0{chapter + 1} / 03</span></div>
        <div className="story-stage"><motion.div className="story-surface" style={reduced ? {} : { scale: surfaceScale }}><MarketChartBackdrop data={data} theme={theme} progress={progress}/></motion.div>
        <div className="story-copy"><AnimatePresence mode="wait"><motion.div key={chapter} initial={{ opacity: 0, y: 18, filter: 'blur(4px)' }} animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }} exit={{ opacity: 0, y: -15, filter: 'blur(4px)' }} transition={{ duration: .4 }}><span className="story-index">0{chapter + 1} — {chapters[chapter].toUpperCase()}</span><h2>{chapter === 0 ? <>Read the<br/><span>movement.</span></> : chapter === 1 ? <>Find the<br/><span>common thread.</span></> : <>Recognize<br/><span>the shift.</span></>}</h2><p>{chapter === 0 ? 'Volatility, correlation, and covariance instability reveal how the market moves as a system.' : chapter === 1 ? 'Thirty industries. A shared underlying force. Principal components make the common movement visible.' : 'As market conditions change, recurring patterns emerge. Three clusters offer a different lens on historical behavior.'}</p></motion.div></AnimatePresence></div>
        <div className="story-card-stack">
          {[0, 1, 2].map(index => <ScrollResearchCard key={index} progress={progress} index={index}>
            <span className="landing-kicker">{['THE DATA FOUNDATION', 'THE COMMON MARKET FACTOR', 'HISTORICAL MARKET STATES'][index]}</span>
            {index === 0 ? <><div className="story-card-number">{number(data.observations)}<small>daily observations</small></div><div className="story-card-rule"/><div className="foundation-row"><span>30 industries</span><span>100 years</span><span>One dataset</span></div><div className="foundation-lines" aria-hidden="true">{recentVolatility.map((point, i) => <span key={i} style={{ height: `${Math.max(5, point.vol_20 / maxRecentVolatility * 100)}%` }}/>)}</div><p>Recent volatility · 22 month-end snapshots</p></> : index === 1 ? <><div className="story-card-number">{data.pca[0].variance.toFixed(2)}<small>% explained by PC1</small></div><div className="factor-bars">{data.pca.map((pc, i) => <div key={pc.name}><span>{pc.name}</span><div><i style={{ width: `${pc.variance / 65 * 100}%`, opacity: i === 0 ? 1 : .35 }}/></div><b>{pc.variance.toFixed(2)}%</b></div>)}</div><p>First 5 PCs explain {data.pca.at(-1).cumulative.toFixed(2)}% of return variance.</p></> : <><div className="story-card-number">03<small>distinct historical clusters</small></div><div className="story-clusters">{data.clusters.map((c, i) => <div key={c.id}><span><i style={{ opacity: 1 - i * .23 }}/>Cluster {c.id}</span><b>{number(c.count)}</b><small>{(c.count / clusterTotal * 100).toFixed(1)}%</small></div>)}</div><p>Full-sample K-means · Descriptive research</p></>}
          </ScrollResearchCard>)}
        </div></div>
        <div className="story-bottom"><ContinuousTabs options={chapters} value={chapters[chapter]} onChange={selectChapter} label="Research chapters"/><div className="story-track"><motion.span style={{ scaleX: progress }}/></div><span>SCROLL TO CONTINUE <ArrowDown size={12}/></span></div>
      </div>
    </section>
    <Preview data={data} onEnter={onEnter}/>
    <AboutSection/>
    <footer className="landing-footer"><a className="landing-brand" href="#"><ChartNoAxesCombined size={21}/>Reg<span>X</span></a><span>Regime-aware portfolio risk research</span><span>Historical analysis · Data through {data.endDate.slice(0, 7)}<br/>Chart animations replay a fixed historical return index.</span></footer>
  </div>;
}
