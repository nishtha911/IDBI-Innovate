import { useParams, useLocation } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import clsx from 'clsx';
// pdf import removed — using html2pdf.js dynamically

const mockData = {
  score: 72,
  riskCategory: 'Amber', // Green, Amber, Red
  components: [
    { subject: 'Cash Flow', A: 80, fullMark: 100 },
    { subject: 'GST Compliance', A: 90, fullMark: 100 },
    { subject: 'EPFO Health', A: 60, fullMark: 100 },
    { subject: 'Credit History', A: 75, fullMark: 100 },
    { subject: 'Market Risk', A: 55, fullMark: 100 },
  ],
  strengths: [
    'Consistent GST filing for the past 12 months.',
    'Strong positive cash flow in the primary operating account.',
  ],
  risks: [
    'High employee attrition indicated by EPFO records.',
    'Sectorial headwinds in the current market environment.',
  ],
  recommendation: 'Approve with standard conditions. Monitor quarterly cash flows.',
  ai_summary: 'Based on the robust GST compliance and healthy cash flow, the MSME exhibits strong financial stability. The amber risk rating is primarily due to sectoral headwinds and EPFO attrition, which should be monitored, but the overall credit profile remains suitable for standard approval limits.',
};

const AssessmentResult = () => {
  const { id } = useParams();
  const location = useLocation();
  const apiResult = location.state?.result;
  
  // Use backend data if available, otherwise fallback to mock
  const data = apiResult ? {
    score: Math.round(apiResult.composite_score),
    riskCategory: apiResult.category,
    components: [
      { subject: 'Revenue Stability', A: apiResult.breakdown?.revenue_stability ?? 0, fullMark: 100 },
      { subject: 'Tax Compliance', A: apiResult.breakdown?.tax_compliance ?? 0, fullMark: 100 },
      { subject: 'Cash Flow', A: apiResult.breakdown?.cash_flow_health ?? 0, fullMark: 100 },
      { subject: 'Growth', A: apiResult.breakdown?.growth_trajectory ?? 0, fullMark: 100 },
      { subject: 'Confidence', A: apiResult.confidence_score ?? 0, fullMark: 100 },
    ],
    strengths: apiResult.reason_codes?.filter(rc => rc.type === 'positive').map(rc => rc.text) ?? mockData.strengths,
    risks: apiResult.reason_codes?.filter(rc => rc.type === 'negative').map(rc => rc.text) ?? mockData.risks,
    recommendation: apiResult.recommendation,
    ai_summary: apiResult.ai_summary,
  } : mockData;
  
  const riskColor = 
    data.riskCategory === 'Green' ? 'text-green-600 bg-green-50 border-green-200' :
    data.riskCategory === 'Amber' ? 'text-amber-600 bg-amber-50 border-amber-200' :
    'text-red-600 bg-red-50 border-red-200';
  
  const handleDownloadPDF = async () => {
    const html2pdf = (await import('html2pdf.js')).default;
    const element = document.getElementById('report-content');
    html2pdf()
      .set({
        margin: 8,
        filename: `Assessment_Report_${id}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      })
      .from(element)
      .save();
  };

  return (
    <div className="space-y-6" id="report-content">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Assessment Report</h1>
          <p className="text-gray-500">ID: {id} • Generated on Oct 24, 2026</p>
        </div>
        <button onClick={handleDownloadPDF} className="px-4 py-2 bg-finsight-teal text-white rounded-md font-medium hover:bg-finsight-darkTeal transition-colors">
          Download PDF
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Score Card */}
        <Card className="col-span-1 md:col-span-1 flex flex-col items-center justify-center py-8">
          <div className="text-center mb-4">
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Overall Health Score</p>
            <div className="mt-2 text-6xl font-bold text-gray-800">{data.score}</div>
            <p className="text-xs text-gray-400 mt-1">out of 100</p>
          </div>
          
          <div className={clsx("px-4 py-1.5 rounded-full border text-sm font-semibold flex items-center gap-2", riskColor)}>
            {data.riskCategory === 'Green' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
            {data.riskCategory} Risk
          </div>
        </Card>

        {/* Radar Chart */}
        <Card className="col-span-1 md:col-span-2">
          <CardHeader>Component Breakdown</CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data.components}>
                <PolarGrid stroke="#E5E7EB" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#4B5563', fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                <Radar name="Score" dataKey="A" stroke="#008479" fill="#008479" fillOpacity={0.4} />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="text-green-700 bg-green-50/50">Key Strengths</CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {data.strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2">
                  <CheckCircle2 size={18} className="text-green-600 mt-0.5 shrink-0" />
                  <span className="text-gray-700">{s}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="text-amber-700 bg-amber-50/50">Identified Risks</CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {data.risks.map((r, i) => (
                <li key={i} className="flex items-start gap-2">
                  <AlertTriangle size={18} className="text-amber-600 mt-0.5 shrink-0" />
                  <span className="text-gray-700">{r}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      <Card className="border-finsight-teal/20 bg-finsight-teal/5">
        <CardHeader className="flex flex-row items-center gap-2">
          <Info size={20} className="text-finsight-teal" />
          Credit Recommendation
        </CardHeader>
        <CardContent>
          <p className="text-gray-800 font-medium text-lg mb-4">{data.recommendation}</p>
          {data.ai_summary && (
            <div className="bg-white p-4 rounded-md border border-finsight-teal/20 shadow-sm">
              <p className="text-xs uppercase font-bold text-finsight-teal mb-2 flex items-center gap-2">
                <span>AI Risk Analyst Summary</span>
                <span className="bg-finsight-orange text-white px-1.5 py-0.5 rounded text-[10px]">GROQ POWERED</span>
              </p>
              <p className="text-gray-600 text-sm italic">"{data.ai_summary}"</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AssessmentResult;
