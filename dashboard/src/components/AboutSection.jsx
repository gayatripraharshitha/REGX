import { ArrowUpRight, Braces, Database, Network } from 'lucide-react';

export default function AboutSection() {
  return <section className="about-regx" id="about-regx" aria-labelledby="about-title">
    <div className="about-heading"><span className="landing-kicker">ABOUT REGX</span><h2 id="about-title">A better understanding<br/>of connected markets.</h2><p>RegX is a regime-aware portfolio risk research project. It connects market structure with covariance estimation, portfolio optimization, and walk-forward evaluation.</p></div>
    <div className="about-details"><blockquote>“A clearer view begins with understanding what moves together.”<cite>The research philosophy behind RegX</cite></blockquote><div className="about-facts"><p><Database size={20}/><span><strong>A century of evidence</strong>Daily returns from 30 Kenneth French industry portfolios.</span></p><p><Network size={20}/><span><strong>Structure before signals</strong>Volatility, correlation, PCA, and descriptive market regimes.</span></p><p><Braces size={20}/><span><strong>Results you can inspect</strong>Seven portfolio strategies share one reproducible research pipeline.</span></p></div><a className="repo-link" href="https://github.com/gayatripraharshitha/REGX" target="_blank" rel="noreferrer">View the project on GitHub <ArrowUpRight size={18}/></a></div>
  </section>;
}
