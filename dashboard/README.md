# RegX Dashboard

React + Vite, Recharts, Motion for React, and an adapted Watermelon UI Continuous
Tabs component. Inter for UI text and DM Mono for labels. Fonts fall back to system
fonts if Google Fonts is unavailable. Light mode is pearl/lavender-gray with soft
lilac/rose washes, plum typography, and muted mulberry accents; dark mode is near black
with muted sage-green accents. Each page load starts in light mode. Separate Light
and Dark buttons change the theme for the current visit, including navigation
between the landing page and workspace.

The home page is a scroll-led research introduction with an original procedural
market-chart backdrop, three research chapters, and a perspective workspace
preview. Monthly candlestick ranges and a line reveal respond to scroll, with
historical regime shading in the last chapter. This uses an equal-weight industry
return index computed from the last 1,260 daily observations, rebased to 100;
it is not an exchange-traded stock quote or a live price feed. Monthly OHLC is
computed from daily index closes. The chart cursor moves across this fixed
history. A static full chart is shown for reduced-motion preferences.
Motion's `useScroll`, `useSpring`, and `useTransform` link the transitions to
scroll position. Research cards adapt Watermelon UI Fund Widget's perspective
and progressive-blur composition. Reduced-motion preferences switch the story
to static cards; no pinned scroll sequence is required in that mode.

The first-screen primary action is **Scroll to explore**. Dashboard entry follows
the research story, in the workspace preview. The workspace has a collapsible
top menu with Overview, Market features, PCA analysis, Market regimes, Industry
connections, and About RegX. The labeled correlation matrix has its own page,
with a persistent selected-pair value, horizontal scrolling on smaller screens,
and touch/keyboard interaction. About includes the project repository link.

Click **Explore the full dashboard** to enter the workspace, or open `/#dashboard`
directly. Click the RegX logo in the workspace to return to the introduction.

## Run on Windows

From the `RegX` folder in PowerShell:

```powershell
cd dashboard
npm.cmd ci
npm.cmd run dev
```

Open the Local URL Vite prints (normally http://127.0.0.1:5173).
Use `npm.cmd` because Windows may block the PowerShell `npm.ps1` shim.
Node.js 22.12+ or 24 LTS is recommended.

## Refresh the research snapshot

The checked-in `public/data/dashboard.json` allows the website to work without a
Python server. To refresh it, run from `RegX`, before building:

```powershell
.\.venv\Scripts\python.exe export_dashboard.py
```

This invokes `load_data`, `create_market_features`, `run_pca`, `run_clustering`,
and `summarize_clusters` from the existing Python modules. It does not run the
portfolio backtest. Calculations use all daily rows; time charts display the last
available observation of each month. Volatility is daily standard deviation in
percent, not annualized. Correlation matrix uses full-history daily returns.
Regime counts use all eligible days, not monthly chart samples. Initial rolling
feature warm-up rows are excluded. Model fits are full-sample descriptive analysis.

Recomputed PCA/cluster results are authoritative; they can differ from manually
copied figures or change after dataset/library updates. Cluster IDs have no
inherent ordering or economic label.

## Deploy to Vercel

1. Commit the `dashboard` directory, including `package-lock.json` and
   `public/data/dashboard.json`, to your GitHub repository. Also commit
   `export_dashboard.py` to preserve the regeneration workflow.
2. In Vercel select **Add New → Project**, import your REGX GitHub repository,
   and choose the branch containing these files.
3. Set **Root Directory** to **dashboard**. The repository itself starts at
   `RegX`, so do not use `RegX/dashboard` unless that extra directory is actually
   present in GitHub.
4. Select framework **Vite**, install command `npm ci`, build command
   `npm run build`, and output directory `dist`. No environment variables needed.
5. Deploy. Each later push to the selected production branch rebuilds the site.

Do not upload `.venv`, `node_modules`, raw CSVs, or Python modules to run the web
frontend. Vercel serves the generated research snapshot bundled with the static
site. Refresh JSON locally, commit it, and redeploy when research data changes.

## Check the production build locally

```powershell
npm.cmd run build
npm.cmd run preview
```

Verify navigation, metric/date filters, hover tooltips, theme toggle, CSV export,
snapshot download, industry search, and narrow-screen navigation. Exports follow
the selected chart date range. PCA, regime counts, and the correlation matrix
always describe the full historical dataset.

Watermelon UI uses copy-in source, not an installed `watermelon-ui` runtime
package. See `THIRD_PARTY_NOTICES.md`. “Motion AI UI” was interpreted as Motion
for React, the documented animation dependency used by Watermelon UI.
