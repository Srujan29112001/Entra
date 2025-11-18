/**
 * PDF Export functionality for reports.
 */

export interface ReportData {
  companyName: string;
  reportDate: string;
  sections: ReportSection[];
}

export interface ReportSection {
  title: string;
  content: string | any[];
  type: "text" | "table" | "metrics";
}

/**
 * Export dashboard data as PDF report.
 *
 * Note: This uses the browser's print functionality.
 * For production, consider using jsPDF or PDFKit.
 */
export async function exportDashboardToPDF(data: any) {
  // Create a printable HTML view
  const printWindow = window.open("", "_blank");

  if (!printWindow) {
    alert("Please allow popups to export PDF");
    return;
  }

  const html = generateReportHTML(data);

  printWindow.document.write(html);
  printWindow.document.close();

  // Wait for content to load, then print
  setTimeout(() => {
    printWindow.print();
  }, 500);
}

function generateReportHTML(data: any): string {
  const { company, financials, metrics } = data;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Business Report - ${company?.name || "Company"}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Arial', sans-serif;
      line-height: 1.6;
      color: #333;
      background: white;
      padding: 40px;
    }

    .header {
      border-bottom: 3px solid #3b82f6;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }

    .header h1 {
      font-size: 32px;
      color: #1e40af;
      margin-bottom: 10px;
    }

    .header .subtitle {
      font-size: 14px;
      color: #64748b;
    }

    .section {
      margin-bottom: 30px;
      page-break-inside: avoid;
    }

    .section h2 {
      font-size: 20px;
      color: #1e40af;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 10px;
      margin-bottom: 15px;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin: 20px 0;
    }

    .metric-card {
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 15px;
      background: #f8fafc;
    }

    .metric-label {
      font-size: 12px;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 5px;
    }

    .metric-value {
      font-size: 24px;
      font-weight: bold;
      color: #1e293b;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
    }

    th {
      background: #f1f5f9;
      padding: 12px;
      text-align: left;
      font-weight: 600;
      color: #475569;
      border-bottom: 2px solid #cbd5e1;
    }

    td {
      padding: 10px 12px;
      border-bottom: 1px solid #e2e8f0;
    }

    tr:hover {
      background: #f8fafc;
    }

    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 2px solid #e2e8f0;
      text-align: center;
      color: #64748b;
      font-size: 12px;
    }

    @media print {
      body {
        padding: 20px;
      }

      .section {
        page-break-inside: avoid;
      }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>${company?.name || "Company Report"}</h1>
    <div class="subtitle">
      Business Intelligence Report | ${new Date().toLocaleDateString()} |
      ${company?.industry || ""} | ${company?.country || ""}
    </div>
  </div>

  <div class="section">
    <h2>Key Metrics</h2>
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-label">Cash Balance</div>
        <div class="metric-value">$${((metrics?.cashBalance || 0) / 1000).toFixed(0)}K</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Monthly Revenue</div>
        <div class="metric-value">$${((metrics?.monthlyRevenue || 0) / 1000).toFixed(0)}K</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Burn Rate</div>
        <div class="metric-value">$${((metrics?.burnRate || 0) / 1000).toFixed(0)}K</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Runway</div>
        <div class="metric-value">${(metrics?.runway || 0).toFixed(1)} mo</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Financial Overview</h2>
    <table>
      <thead>
        <tr>
          <th>Metric</th>
          <th>Current Value</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Cash Position</td>
          <td>$${((financials?.cash_balance || 0) / 1000).toFixed(0)}K</td>
          <td>${(financials?.runway_months || 0) > 6 ? "Healthy" : "Attention Needed"}</td>
        </tr>
        <tr>
          <td>Monthly Revenue</td>
          <td>$${((financials?.monthly_revenue || 0) / 1000).toFixed(0)}K</td>
          <td>Growing</td>
        </tr>
        <tr>
          <td>Monthly Expenses</td>
          <td>$${((financials?.monthly_expenses || 0) / 1000).toFixed(0)}K</td>
          <td>Controlled</td>
        </tr>
        <tr>
          <td>LTV:CAC Ratio</td>
          <td>${((financials?.ltv || 0) / Math.max(financials?.cac || 1, 1)).toFixed(2)}</td>
          <td>${((financials?.ltv || 0) / Math.max(financials?.cac || 1, 1)) >= 3 ? "Excellent" : "Needs Improvement"}</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>Recommendations</h2>
    <ul>
      ${(metrics?.runway || 0) < 6 ? "<li><strong>Critical:</strong> Runway below 6 months. Consider raising funds or reducing burn rate immediately.</li>" : ""}
      ${((financials?.ltv || 0) / Math.max(financials?.cac || 1, 1)) < 3 ? "<li><strong>Unit Economics:</strong> LTV:CAC ratio below 3:1. Focus on improving customer lifetime value or reducing acquisition costs.</li>" : ""}
      <li>Continue monitoring cash flow and adjust spending as needed.</li>
      <li>Consider scenario planning for different growth trajectories.</li>
      <li>Consult with your AI advisors for personalized strategic guidance.</li>
    </ul>
  </div>

  <div class="footer">
    Generated by Entra AI Advisory Platform | ${new Date().toLocaleString()}
    <br>
    Confidential - For Internal Use Only
  </div>
</body>
</html>
  `;
}

/**
 * Export scenario comparison report.
 */
export async function exportScenarioComparison(scenarios: any[]) {
  const printWindow = window.open("", "_blank");

  if (!printWindow) {
    alert("Please allow popups to export PDF");
    return;
  }

  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Scenario Comparison Report</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 40px; }
    h1 { color: #1e40af; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background: #f1f5f9; padding: 12px; text-align: left; border-bottom: 2px solid #cbd5e1; }
    td { padding: 10px; border-bottom: 1px solid #e2e8f0; }
  </style>
</head>
<body>
  <h1>Scenario Comparison Report</h1>
  <table>
    <thead>
      <tr>
        <th>Scenario</th>
        <th>Growth Rate</th>
        <th>Funding</th>
        <th>Final Cash</th>
        <th>Final Revenue</th>
      </tr>
    </thead>
    <tbody>
      ${scenarios.map(s => `
        <tr>
          <td><strong>${s.name}</strong></td>
          <td>${(s.growth_rate * 100).toFixed(1)}%</td>
          <td>$${(s.funding_amount / 1000).toFixed(0)}K</td>
          <td>$${((s.projections?.[s.projections.length - 1]?.cash || 0) / 1000).toFixed(0)}K</td>
          <td>$${((s.projections?.[s.projections.length - 1]?.revenue || 0) / 1000).toFixed(0)}K</td>
        </tr>
      `).join("")}
    </tbody>
  </table>
  <div style="margin-top: 40px; color: #64748b; font-size: 12px; text-align: center;">
    Generated ${new Date().toLocaleString()}
  </div>
</body>
</html>
  `;

  printWindow.document.write(html);
  printWindow.document.close();

  setTimeout(() => {
    printWindow.print();
  }, 500);
}
