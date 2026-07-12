/**
 * Opens a print dialog with a clean, professionally formatted PDF report.
 * All styling is self-contained — no Tailwind, no broken icons.
 */

const PRINT_STYLES = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; color: #1f2937; padding: 32px; font-size: 13px; }
  .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #008479; padding-bottom: 16px; margin-bottom: 24px; }
  .logo { font-size: 22px; font-weight: 800; color: #008479; letter-spacing: -0.5px; }
  .logo span { color: #ed752c; }
  .header-sub { font-size: 11px; color: #6b7280; margin-top: 3px; }
  .header-meta { text-align: right; font-size: 11px; color: #6b7280; line-height: 1.6; }
  .section-title { font-size: 12px; font-weight: 700; color: #374151; text-transform: uppercase; letter-spacing: 0.08em; margin: 20px 0 10px; padding-bottom: 6px; border-bottom: 1px solid #e5e7eb; }
  .metrics { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 20px; }
  .metric { border: 1px solid #e5e7eb; border-radius: 6px; padding: 12px 10px; }
  .metric .label { font-size: 9px; color: #6b7280; text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em; }
  .metric .val { font-size: 22px; font-weight: 800; color: #1f2937; margin: 4px 0 2px; }
  .metric .trend-up { font-size: 10px; color: #16a34a; }
  .metric .trend-down { font-size: 10px; color: #dc2626; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px; }
  thead { background: #f9fafb; }
  th { padding: 8px 10px; text-align: left; font-size: 9px; text-transform: uppercase; color: #6b7280; font-weight: 700; letter-spacing: 0.06em; border-bottom: 2px solid #e5e7eb; }
  td { padding: 8px 10px; border-bottom: 1px solid #f3f4f6; color: #374151; }
  .mono { font-family: 'Courier New', monospace; color: #6b7280; font-size: 11px; }
  .bold { font-weight: 700; color: #1f2937; }
  .green { color: #16a34a; font-weight: 700; }
  .amber { color: #d97706; font-weight: 700; }
  .red { color: #dc2626; font-weight: 700; }
  .badge { display: inline-block; padding: 2px 7px; border-radius: 999px; font-size: 9px; font-weight: 700; text-transform: uppercase; }
  .badge-green { background: #dcfce7; color: #15803d; }
  .badge-red { background: #fee2e2; color: #b91c1c; }
  .badge-amber { background: #fef9c3; color: #92400e; }
  .score-box { text-align: center; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
  .score-big { font-size: 64px; font-weight: 900; color: #008479; line-height: 1; }
  .score-label { font-size: 11px; color: #6b7280; margin-top: 4px; }
  .risk-badge { display: inline-block; margin-top: 10px; padding: 5px 18px; border-radius: 999px; font-size: 12px; font-weight: 700; border: 2px solid; }
  .risk-green { color: #16a34a; border-color: #16a34a; background: #f0fdf4; }
  .risk-amber { color: #d97706; border-color: #d97706; background: #fffbeb; }
  .risk-red { color: #dc2626; border-color: #dc2626; background: #fef2f2; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
  .panel { border: 1px solid #e5e7eb; border-radius: 6px; padding: 14px; }
  .panel-title { font-size: 10px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.06em; margin-bottom: 10px; }
  .panel-title.green-t { color: #16a34a; }
  .panel-title.red-t { color: #dc2626; }
  ul { list-style: none; padding: 0; }
  ul li { padding: 5px 0; border-bottom: 1px solid #f3f4f6; font-size: 12px; color: #374151; }
  ul li:before { content: '• '; color: #008479; font-weight: 900; }
  .ai-box { background: #f0fdf9; border: 1px solid #a7f3d0; border-radius: 6px; padding: 14px; margin-bottom: 20px; }
  .ai-label { font-size: 10px; text-transform: uppercase; font-weight: 700; color: #008479; letter-spacing: 0.06em; margin-bottom: 6px; }
  .ai-text { font-size: 12px; color: #374151; font-style: italic; line-height: 1.6; }
  .rec-box { background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 14px; }
  .rec-label { font-size: 10px; font-weight: 700; color: #92400e; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
  .rec-text { font-size: 13px; font-weight: 600; color: #1f2937; }
  .footer { margin-top: 28px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 10px; color: #9ca3af; display: flex; justify-content: space-between; }
  @media print { body { padding: 18px; } @page { margin: 1cm; } }
`;

function printWindow(html, title) {
  const w = window.open('', '_blank');
  w.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>${title}</title><style>${PRINT_STYLES}</style></head><body>${html}</body></html>`);
  w.document.close();
  w.focus();
  setTimeout(() => { w.print(); w.close(); }, 700);
}

export function exportDashboardPDF(metrics) {
  const today = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
  const assessments = [
    { id: 'FS-2026-8921', name: 'TechVision IT Solutions Pvt Ltd', sector: 'IT/Tech', score: 85, status: 'Approved', analyst: 'A. Sharma' },
    { id: 'FS-2026-8920', name: 'GreenField Agri Corp', sector: 'Manufacturing', score: 42, status: 'Rejected', analyst: 'Auto' },
    { id: 'FS-2026-8919', name: 'Metro Builders LLP', sector: 'Real Estate', score: 68, status: 'Under Review', analyst: 'M. Patel' },
    { id: 'FS-2026-8918', name: 'Sunrise Logistics', sector: 'Services', score: 72, status: 'Approved', analyst: 'Auto' },
    { id: 'FS-2026-8917', name: 'Apex Retailers', sector: 'Retail', score: 55, status: 'Under Review', analyst: 'K. Singh' },
  ];

  const badgeClass = (s) => s === 'Approved' ? 'badge-green' : s === 'Rejected' ? 'badge-red' : 'badge-amber';
  const scoreClass = (s) => s >= 75 ? 'green' : s >= 50 ? 'amber' : 'red';

  const html = `
    <div class="header">
      <div>
        <div class="logo">Fin<span>Sight</span></div>
        <div class="header-sub">Executive Dashboard Report</div>
      </div>
      <div class="header-meta">
        IDBI Bank Limited<br/>
        Generated: ${today}<br/>
        <strong>CONFIDENTIAL</strong>
      </div>
    </div>

    <div class="section-title">Portfolio Metrics</div>
    <div class="metrics">
      <div class="metric"><div class="label">Total Assessments</div><div class="val">${metrics?.totalAssessments || '12,450'}</div><div class="trend-up">↑ +12.4% MoM</div></div>
      <div class="metric"><div class="label">Avg Portfolio Score</div><div class="val">${metrics?.avgScore || '68.4'}</div><div class="trend-up">↑ +3.2 pts</div></div>
      <div class="metric"><div class="label">High Risk Entities</div><div class="val">${metrics?.highRisk || '142'}</div><div class="trend-down">↓ -5.1% MoM</div></div>
      <div class="metric"><div class="label">Pending Reviews</div><div class="val">45</div></div>
      <div class="metric"><div class="label">Automated Approvals</div><div class="val">89%</div><div class="trend-up">↑ +2.1%</div></div>
    </div>

    <div class="section-title">Recent Assessment Queue</div>
    <table>
      <thead><tr><th>ID</th><th>Entity Name</th><th>Sector</th><th>Score</th><th>Status</th><th>Analyst</th></tr></thead>
      <tbody>
        ${assessments.map(a => `<tr>
          <td class="mono">${a.id}</td>
          <td class="bold">${a.name}</td>
          <td>${a.sector}</td>
          <td class="${scoreClass(a.score)}">${a.score}</td>
          <td><span class="badge ${badgeClass(a.status)}">${a.status}</span></td>
          <td>${a.analyst}</td>
        </tr>`).join('')}
      </tbody>
    </table>

    <div class="section-title">Critical Alerts</div>
    <table>
      <thead><tr><th>Type</th><th>Details</th></tr></thead>
      <tbody>
        <tr><td class="red bold">API Latency Warning</td><td>GSTIN fetching latency &gt; 2s for 15 requests.</td></tr>
        <tr><td class="amber bold">Manual Reviews Overdue</td><td>7 applications pending analyst review &gt; 48 hrs.</td></tr>
        <tr><td style="color:#3b82f6;font-weight:700;">Compliance Update</td><td>New KYC norms active. Ensure parameter update.</td></tr>
      </tbody>
    </table>

    <div class="footer">
      <span>FinSight Enterprise Assessment Platform &nbsp;|&nbsp; IDBI Bank Limited</span>
      <span>Confidential &mdash; For Internal Use Only</span>
    </div>
  `;
  printWindow(html, 'Executive Dashboard Report — FinSight');
}

export function exportAssessmentPDF(id, data) {
  const today = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
  const riskClass = data.riskCategory === 'Green' ? 'risk-green' : data.riskCategory === 'Amber' ? 'risk-amber' : 'risk-red';

  const html = `
    <div class="header">
      <div>
        <div class="logo">Fin<span>Sight</span></div>
        <div class="header-sub">MSME Credit Assessment Report</div>
      </div>
      <div class="header-meta">
        IDBI Bank Limited<br/>
        Assessment ID: <strong>${id}</strong><br/>
        Generated: ${today}<br/>
        <strong>CONFIDENTIAL</strong>
      </div>
    </div>

    <div class="score-box">
      <div class="score-label">Overall Financial Health Score</div>
      <div class="score-big">${data.score}</div>
      <div class="score-label">out of 100</div>
      <div><span class="risk-badge ${riskClass}">${data.riskCategory} Risk</span></div>
    </div>

    <div class="two-col">
      <div class="panel">
        <div class="panel-title green-t">Key Strengths</div>
        <ul>${data.strengths.map(s => `<li>${s}</li>`).join('')}</ul>
      </div>
      <div class="panel">
        <div class="panel-title red-t">Identified Risks</div>
        <ul>${data.risks.map(r => `<li>${r}</li>`).join('')}</ul>
      </div>
    </div>

    <div class="section-title">Score Breakdown</div>
    <table>
      <thead><tr><th>Component</th><th>Score</th></tr></thead>
      <tbody>
        ${data.components.map(c => `<tr>
          <td class="bold">${c.subject}</td>
          <td class="${c.A >= 75 ? 'green' : c.A >= 50 ? 'amber' : 'red'}">${c.A} / 100</td>
        </tr>`).join('')}
      </tbody>
    </table>

    ${data.ai_summary ? `
    <div class="ai-box">
      <div class="ai-label">AI Risk Analyst Summary</div>
      <div class="ai-text">&ldquo;${data.ai_summary}&rdquo;</div>
    </div>` : ''}

    <div class="rec-box">
      <div class="rec-label">Credit Recommendation</div>
      <div class="rec-text">${data.recommendation}</div>
    </div>

    <div class="footer">
      <span>FinSight Enterprise Assessment Platform &nbsp;|&nbsp; IDBI Bank Limited</span>
      <span>Confidential &mdash; For Internal Use Only</span>
    </div>
  `;
  printWindow(html, `Assessment Report ${id} — FinSight`);
}
