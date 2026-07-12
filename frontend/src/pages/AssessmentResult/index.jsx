import { useParams } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import clsx from 'clsx';
import html2pdf from 'html2pdf.js';

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
};

const AssessmentResult = () => {
  const { id } = useParams();
  
  const riskColor = 
    mockData.riskCategory === 'Green' ? 'text-green-600 bg-green-50 border-green-200' :
    mockData.riskCategory === 'Amber' ? 'text-amber-600 bg-amber-50 border-amber-200' :
    'text-red-600 bg-red-50 border-red-200';

  const handleDownloadPDF = () => {
    const element = document.getElementById('report-content');
    const opt = {
      margin: 0.5,
      filename: `Assessment_Report_${id}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
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
            <div className="mt-2 text-6xl font-bold text-gray-800">{mockData.score}</div>
            <p className="text-xs text-gray-400 mt-1">out of 100</p>
          </div>
          
          <div className={clsx("px-4 py-1.5 rounded-full border text-sm font-semibold flex items-center gap-2", riskColor)}>
            {mockData.riskCategory === 'Green' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
            {mockData.riskCategory} Risk
          </div>
        </Card>

        {/* Radar Chart */}
        <Card className="col-span-1 md:col-span-2">
          <CardHeader>Component Breakdown</CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={mockData.components}>
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
              {mockData.strengths.map((s, i) => (
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
              {mockData.risks.map((r, i) => (
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
          <p className="text-gray-800 font-medium text-lg">{mockData.recommendation}</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default AssessmentResult;
