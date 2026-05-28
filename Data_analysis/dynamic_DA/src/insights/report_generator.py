"""
Report Generator
================
Produces a professional HTML analytical report and a plain-text summary
report from all pipeline artefacts.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from config.settings import REPORTS_DIR, VISUALIZATIONS_DIR
from src.utils.logger import get_logger
from src.utils.console import print_info, print_success

logger = get_logger(__name__)


class ReportGenerator:
    """
    Generates the final HTML + TXT analytical report.

    Args:
        insights: Dict produced by InsightGenerator.
        quality_report: Serialised quality report dict.
        metadata: Dataset metadata dict.
        plot_paths_before: List of pre-processing plot file paths.
        plot_paths_after: List of post-processing plot file paths.
        processing_log: List of preprocessing step messages.
    """

    def __init__(
        self,
        insights: Dict[str, Any],
        quality_report: Dict[str, Any],
        metadata: Dict[str, Any],
        plot_paths_before: List[Path],
        plot_paths_after: List[Path],
        processing_log: List[str],
    ) -> None:
        self.insights = insights
        self.qr = quality_report
        self.metadata = metadata
        self.plots_before = plot_paths_before
        self.plots_after = plot_paths_after
        self.processing_log = processing_log
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ts_slug = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def generate(self) -> Dict[str, Path]:
        """
        Generate both HTML and TXT reports.

        Returns:
            Dict with keys 'html' and 'txt' mapping to saved file paths.
        """
        print_info("Generating analytical reports …")
        paths = {
            "html": self._write_html(),
            "txt":  self._write_txt(),
            "json": self._write_json(),
        }
        print_success("Reports saved to reports/ directory.")
        return paths

    # ──────────────────────────────────────────
    # HTML report
    # ──────────────────────────────────────────

    def _write_html(self) -> Path:
        """Build and write a self-contained HTML report."""
        html = self._build_html()
        path = REPORTS_DIR / f"analytics_report_{self.ts_slug}.html"
        path.write_text(html, encoding="utf-8")
        logger.info("HTML report saved: %s", path)
        return path

    def _build_html(self) -> str:
        domain = self.insights.get("domain", "General Business")
        quality_score = self.qr.get("overall_quality_score", "N/A")

        # ── Stats section ──────────────────────
        summary = self.insights.get("dataset_summary", {})
        summary_rows = "".join(
            f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>"
            for k, v in summary.items()
        )

        # ── Quality section ────────────────────
        null_pct = self.qr.get("null_pct_report", {})
        null_rows = "".join(
            f"<tr><td>{col}</td><td>{pct}%</td>"
            f"<td>{'⚠' if pct > 20 else '✔'}</td></tr>"
            for col, pct in list(null_pct.items())[:30]
        )

        # ── Insights section ───────────────────
        def _list_html(items):
            if isinstance(items, list):
                return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
            if isinstance(items, dict):
                return "<ul>" + "".join(
                    f"<li><strong>{k}:</strong> {v}</li>" for k, v in items.items()
                ) + "</ul>"
            return f"<p>{items}</p>"

        trends_html     = _list_html(self.insights.get("trends", []))
        corr_html       = _list_html(self.insights.get("correlations", []))
        risks_html      = _list_html(self.insights.get("risk_factors", []))
        patterns_html   = _list_html(self.insights.get("patterns", []))
        forecast_html   = _list_html(self.insights.get("forecasting_notes", []))
        ops_html        = _list_html(self.insights.get("operational_insights", []))
        recs_html       = _list_html(self.insights.get("recommendations", []))

        # ── Images ────────────────────────────
        def _img_tag(p: Path) -> str:
            rel = p.relative_to(REPORTS_DIR.parent) if p.exists() else p
            return (
                f'<figure>'
                f'<img src="../{rel}" alt="{p.stem}" loading="lazy">'
                f'<figcaption>{p.stem.replace("_", " ").title()}</figcaption>'
                f'</figure>'
            )

        before_imgs = "\n".join(_img_tag(p) for p in self.plots_before if p and p.exists())
        after_imgs  = "\n".join(_img_tag(p) for p in self.plots_after  if p and p.exists())

        # ── Preprocessing log ──────────────────
        log_html = "".join(f"<li>{entry}</li>" for entry in self.processing_log)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Analytics Pipeline Report — {domain}</title>
<style>
  :root {{
    --primary: #2563eb; --bg: #f8fafc; --card: #ffffff;
    --text: #1e293b; --muted: #64748b; --border: #e2e8f0;
    --green: #16a34a; --red: #dc2626; --yellow: #d97706;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg);
          color: var(--text); line-height: 1.6; }}
  header {{ background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
            color: white; padding: 2.5rem 2rem; text-align: center; }}
  header h1 {{ font-size: 2rem; font-weight: 700; }}
  header p  {{ opacity: .85; margin-top: .4rem; }}
  .badge {{ display:inline-block; background:rgba(255,255,255,.2);
            border-radius: 1rem; padding: .25rem .9rem;
            font-size: .85rem; margin-top: .8rem; }}
  main {{ max-width: 1200px; margin: 2rem auto; padding: 0 1.5rem; }}
  .card {{ background: var(--card); border: 1px solid var(--border);
           border-radius: 12px; padding: 1.8rem; margin-bottom: 1.8rem;
           box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
  h2 {{ color: var(--primary); font-size: 1.3rem; margin-bottom: 1rem;
        border-bottom: 2px solid var(--border); padding-bottom: .5rem; }}
  h3 {{ color: var(--text); font-size: 1.05rem; margin: 1.2rem 0 .6rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
  th {{ background: var(--primary); color: white; padding: .6rem 1rem; text-align: left; }}
  td {{ padding: .5rem 1rem; border-bottom: 1px solid var(--border); }}
  tr:nth-child(even) td {{ background: #f1f5f9; }}
  ul {{ padding-left: 1.5rem; }}
  li {{ margin: .35rem 0; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(480px, 1fr)); gap: 1.2rem; }}
  figure {{ background: var(--card); border: 1px solid var(--border);
            border-radius: 10px; overflow: hidden; }}
  figure img {{ width: 100%; height: auto; display: block; }}
  figcaption {{ padding: .5rem .8rem; font-size: .8rem; color: var(--muted);
                text-align: center; background: #f8fafc; }}
  .score {{ font-size: 2.5rem; font-weight: 700; color: var(--primary); }}
  .meta {{ display: flex; flex-wrap: wrap; gap: 1rem; }}
  .meta-item {{ flex: 1; min-width: 140px; background: #f1f5f9;
               border-radius: 8px; padding: .8rem; text-align: center; }}
  .meta-item span {{ display: block; font-size: .75rem; color: var(--muted); }}
  .meta-item strong {{ font-size: 1.15rem; }}
  footer {{ text-align: center; padding: 2rem; color: var(--muted); font-size: .85rem; }}
</style>
</head>
<body>
<header>
  <h1>📊 Automated Analytics Pipeline Report</h1>
  <p>Domain: <strong>{domain}</strong> &nbsp;|&nbsp; Generated: {self.timestamp}</p>
  <div class="badge">Data Quality Score: <strong>{quality_score}/100</strong></div>
</header>

<main>

<!-- Dataset Overview -->
<div class="card">
  <h2>📁 Dataset Overview</h2>
  <div class="meta">
    <div class="meta-item"><strong>{summary.get('rows','N/A')}</strong><span>Rows</span></div>
    <div class="meta-item"><strong>{summary.get('columns','N/A')}</strong><span>Columns</span></div>
    <div class="meta-item"><strong>{summary.get('file_size_mb','N/A')} MB</strong><span>File Size</span></div>
    <div class="meta-item"><strong>{summary.get('memory_usage_mb','N/A')} MB</strong><span>Memory Usage</span></div>
    <div class="meta-item"><strong>{summary.get('duplicate_rows','N/A')}</strong><span>Duplicate Rows</span></div>
    <div class="meta-item"><div class="score">{quality_score}</div><span>Quality Score / 100</span></div>
  </div>
  <br>
  <table>
    <thead><tr><th>Attribute</th><th>Value</th></tr></thead>
    <tbody>{summary_rows}</tbody>
  </table>
</div>

<!-- Data Quality -->
<div class="card">
  <h2>🔍 Data Quality Report</h2>
  <h3>Null Percentage by Column</h3>
  <table>
    <thead><tr><th>Column</th><th>Null %</th><th>Status</th></tr></thead>
    <tbody>{null_rows}</tbody>
  </table>
</div>

<!-- Visualisations Before -->
<div class="card">
  <h2>📈 Visualisations — Before Processing</h2>
  <div class="grid">{before_imgs}</div>
</div>

<!-- Visualisations After -->
<div class="card">
  <h2>📊 Visualisations — After Processing</h2>
  <div class="grid">{after_imgs}</div>
</div>

<!-- Trends -->
<div class="card">
  <h2>📉 Detected Trends</h2>
  {trends_html}
</div>

<!-- Correlations -->
<div class="card">
  <h2>🔗 Correlation Insights</h2>
  {corr_html}
</div>

<!-- Patterns -->
<div class="card">
  <h2>🔎 Data Patterns</h2>
  {patterns_html}
</div>

<!-- Risk Factors -->
<div class="card">
  <h2>⚠️ Risk Factors</h2>
  {risks_html}
</div>

<!-- Forecasting -->
<div class="card">
  <h2>🔮 Forecasting Possibilities</h2>
  {forecast_html}
</div>

<!-- Operational Insights -->
<div class="card">
  <h2>⚙️ Operational Insights</h2>
  {ops_html}
</div>

<!-- Recommendations -->
<div class="card">
  <h2>✅ Recommendations for Stakeholders</h2>
  {recs_html}
</div>

<!-- Preprocessing Log -->
<div class="card">
  <h2>🛠️ Preprocessing Log</h2>
  <ul>{log_html}</ul>
</div>

</main>
<footer>
  <p>Generated by <strong>Kaggle Analytics Pipeline</strong> &nbsp;|&nbsp; {self.timestamp}</p>
</footer>
</body>
</html>"""

    # ──────────────────────────────────────────
    # Plain-text report
    # ──────────────────────────────────────────

    def _write_txt(self) -> Path:
        """Write a plain-text summary report."""
        lines = [
            "=" * 80,
            "  AUTOMATED ANALYTICS PIPELINE — REPORT",
            f"  Generated: {self.timestamp}",
            f"  Domain: {self.insights.get('domain', 'N/A')}",
            "=" * 80,
            "",
        ]

        def _section(title: str, items):
            lines.append(f"\n{'─' * 60}")
            lines.append(f"  {title}")
            lines.append("─" * 60)
            if isinstance(items, list):
                for item in items:
                    lines.append(f"  • {item}")
            elif isinstance(items, dict):
                for k, v in items.items():
                    lines.append(f"  {k:<30}: {v}")
            else:
                lines.append(f"  {items}")

        _section("DATASET SUMMARY", self.insights.get("dataset_summary", {}))
        _section("DETECTED TRENDS", self.insights.get("trends", []))
        _section("CORRELATION INSIGHTS", self.insights.get("correlations", []))
        _section("RISK FACTORS", self.insights.get("risk_factors", []))
        _section("DATA PATTERNS", self.insights.get("patterns", []))
        _section("FORECASTING NOTES", self.insights.get("forecasting_notes", []))
        _section("OPERATIONAL INSIGHTS", self.insights.get("operational_insights", []))
        _section("RECOMMENDATIONS", self.insights.get("recommendations", []))
        _section("PREPROCESSING LOG", self.processing_log)

        lines += ["", "=" * 80, "  END OF REPORT", "=" * 80]

        path = REPORTS_DIR / f"analytics_report_{self.ts_slug}.txt"
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("TXT report saved: %s", path)
        return path

    # ──────────────────────────────────────────
    # JSON dump
    # ──────────────────────────────────────────

    def _write_json(self) -> Path:
        """Dump all insights as structured JSON for downstream consumption."""
        payload = {
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "quality_report": self.qr,
            "insights": self.insights,
            "preprocessing_log": self.processing_log,
        }
        path = REPORTS_DIR / f"analytics_report_{self.ts_slug}.json"
        path.write_text(
            json.dumps(payload, indent=2, default=str),
            encoding="utf-8"
        )
        logger.info("JSON report saved: %s", path)
        return path
