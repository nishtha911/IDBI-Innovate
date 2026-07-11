import { useState, useEffect } from 'react';
import { Users, FileWarning, ShieldAlert, TrendingUp, ArrowUpRight, ArrowDownRight, Briefcase, FileText, AlertTriangle, CheckCircle, Clock, FilePlus2 } from 'lucide-react';
import { MetricCard } from '../../components/common/MetricCard';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { getDashboardMetrics } from '../../services/assessments';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Legend, Cell, PieChart, Pie } from 'recharts';
import clsx from 'clsx';

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await getDashboardMetrics();
        setMetrics(data);
      } catch (error) {
        console.error("Failed to load metrics", error);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-finsight-teal font-medium">
        <div className="animate-spin mr-2 border-t-2 border-finsight-teal w-5 h-5 rounded-full"></div>
        Loading Enterprise Dashboard...
      </div>
    );
  }

  const riskData = [
    { name: 'Low Risk', value: 400, color: '#10B981' },
    { name: 'Medium Risk', value: 300, color: '#F59E0B' },
    { name: 'High Risk', value: 150, color: '#EF4444' }
  ];

  const sectorData = [
    { name: 'Manufacturing', val: 40 },
    { name: 'Retail', val: 30 },
    { name: 'Services', val: 20 },
    { name: 'IT/Tech', val: 10 }
  ];

  return (
    <div className="space-y-4 max-w-full">
      {/* Ticker Banner */}
      <div className="bg-finsight-darkTeal text-white text-xs py-1.5 px-4 rounded-md shadow-sm flex items-center overflow-hidden">
        <span className="font-bold bg-finsight-orange text-white px-2 py-0.5 rounded text-[10px] uppercase tracking-wider mr-3 shrink-0">Live Updates</span>
        <div className="whitespace-nowrap animate-marquee flex gap-8">
          <span>FinSight Engine v4 deployed successfully.</span>
          <span>Market alert: RBI announces new MSME classification norms.</span>
          <span>System maintenance scheduled for Sunday 02:00 AM IST.</span>
          <span>New Risk Cohort models updated with latest GSTIN parameters.</span>
        </div>
      </div>

      <div className="flex justify-between items-end border-b border-gray-200 pb-2">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 tracking-tight">Executive Dashboard</h1>
          <p className="text-xs text-gray-500 font-medium">Portfolio Overview & Risk Assessment Metrics</p>
        </div>
        <div className="flex gap-2">
          <button className="text-xs bg-white border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-50 text-gray-700 font-medium transition-colors">Export PDF</button>
          <button className="text-xs bg-finsight-teal text-white px-3 py-1.5 rounded-md hover:bg-finsight-darkTeal font-medium transition-colors shadow-sm">Generate Report</button>
        </div>
      </div>

      {/* Dense Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
        <MetricCard
          title="Total Assessments"
          value={metrics?.totalAssessments || "12,450"}
          icon={Briefcase}
          trend="up"
          trendLabel="+12.4% MoM"
          colorClass="text-finsight-teal bg-finsight-lightTeal"
        />
        <MetricCard
          title="Avg Portfolio Score"
          value={metrics?.avgScore || "68.4"}
          icon={TrendingUp}
          trend="up"
          trendLabel="+3.2 points"
          colorClass="text-blue-600 bg-blue-50"
        />
        <MetricCard
          title="High Risk Entities"
          value={metrics?.highRisk || "142"}
          icon={ShieldAlert}
          trend="down"
          trendLabel="-5.1% MoM"
          colorClass="text-red-600 bg-red-50"
        />
        <MetricCard
          title="Pending Reviews"
          value="45"
          icon={Clock}
          colorClass="text-finsight-orange bg-orange-50"
        />
        <MetricCard
          title="Automated Approvals"
          value="89%"
          icon={CheckCircle}
          trend="up"
          trendLabel="+2.1% efficiency"
          colorClass="text-green-600 bg-green-50"
        />
      </div>

      {/* Dense Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* Left Column: Charts */}
        <div className="lg:col-span-8 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="shadow-sm border-gray-200">
              <CardHeader className="py-2.5 px-4 border-b bg-gray-50/50">
                <span className="text-sm font-bold text-gray-800">Portfolio Health Trend (90 Days)</span>
              </CardHeader>
              <CardContent className="h-48 pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metrics?.recentTrends || [{month: 'Jan', score: 65}, {month: 'Feb', score: 67}, {month: 'Mar', score: 68}]}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 10 }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 10 }} domain={['auto', 'auto']} />
                    <RechartsTooltip contentStyle={{ fontSize: '12px', borderRadius: '4px' }}/>
                    <Line type="monotone" dataKey="score" stroke="#008479" strokeWidth={2} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="shadow-sm border-gray-200">
              <CardHeader className="py-2.5 px-4 border-b bg-gray-50/50">
                <span className="text-sm font-bold text-gray-800">Risk Cohort Distribution</span>
              </CardHeader>
              <CardContent className="h-48 pt-4 pb-0 flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={riskData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={2} dataKey="value">
                      {riskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip contentStyle={{ fontSize: '12px' }}/>
                    <Legend iconType="circle" wrapperStyle={{ fontSize: '10px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Dense Data Table */}
          <Card className="shadow-sm border-gray-200">
            <CardHeader className="py-2.5 px-4 border-b bg-gray-50/50 flex justify-between items-center">
              <span className="text-sm font-bold text-gray-800">Recent Assessments Queue</span>
              <a href="#" className="text-[10px] font-semibold text-finsight-teal hover:underline uppercase tracking-wider">View All</a>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs whitespace-nowrap">
                  <thead className="bg-gray-50 text-gray-500 uppercase font-semibold text-[10px] tracking-wider border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-2">ID</th>
                      <th className="px-4 py-2">Entity Name</th>
                      <th className="px-4 py-2">Sector</th>
                      <th className="px-4 py-2">Score</th>
                      <th className="px-4 py-2">Status</th>
                      <th className="px-4 py-2">Analyst</th>
                      <th className="px-4 py-2 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {[
                      { id: 'FS-2026-8921', name: 'TechVision IT Solutions Pvt Ltd', sector: 'IT/Tech', score: 85, status: 'Approved', analyst: 'A. Sharma' },
                      { id: 'FS-2026-8920', name: 'GreenField Agri Corp', sector: 'Manufacturing', score: 42, status: 'Rejected', analyst: 'Auto' },
                      { id: 'FS-2026-8919', name: 'Metro Builders LLP', sector: 'Real Estate', score: 68, status: 'Under Review', analyst: 'M. Patel' },
                      { id: 'FS-2026-8918', name: 'Sunrise Logistics', sector: 'Services', score: 72, status: 'Approved', analyst: 'Auto' },
                      { id: 'FS-2026-8917', name: 'Apex Retailers', sector: 'Retail', score: 55, status: 'Under Review', analyst: 'K. Singh' },
                    ].map((item, idx) => (
                      <tr key={idx} className="hover:bg-gray-50/80 transition-colors">
                        <td className="px-4 py-2 font-mono text-gray-500">{item.id}</td>
                        <td className="px-4 py-2 font-medium text-gray-800">{item.name}</td>
                        <td className="px-4 py-2 text-gray-600">{item.sector}</td>
                        <td className="px-4 py-2">
                          <span className={clsx("font-bold", item.score >= 75 ? "text-green-600" : item.score >= 50 ? "text-yellow-600" : "text-red-600")}>{item.score}</span>
                        </td>
                        <td className="px-4 py-2">
                          <span className={clsx(
                            "text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider",
                            item.status === 'Approved' ? 'bg-green-100 text-green-700' :
                            item.status === 'Rejected' ? 'bg-red-100 text-red-700' :
                            'bg-yellow-100 text-yellow-700'
                          )}>
                            {item.status}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-gray-500">{item.analyst}</td>
                        <td className="px-4 py-2 text-right">
                          <button className="text-finsight-teal hover:text-finsight-darkTeal font-semibold">Review</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Alerts & Actions */}
        <div className="lg:col-span-4 space-y-4">
          <Card className="shadow-sm border-gray-200">
            <CardHeader className="py-2.5 px-4 border-b bg-gray-50/50">
              <span className="text-sm font-bold text-gray-800">Critical Alerts</span>
            </CardHeader>
            <CardContent className="p-3">
              <ul className="space-y-3">
                <li className="flex gap-3 items-start border-b border-gray-100 pb-3">
                  <AlertTriangle size={16} className="text-red-500 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-gray-800 leading-tight">API Latency Warning</p>
                    <p className="text-[10px] text-gray-500 mt-1">GSTIN fetching latency &gt; 2s for 15 requests.</p>
                  </div>
                </li>
                <li className="flex gap-3 items-start border-b border-gray-100 pb-3">
                  <FileWarning size={16} className="text-finsight-orange mt-0.5 shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-gray-800 leading-tight">Manual Reviews Overdue</p>
                    <p className="text-[10px] text-gray-500 mt-1">7 applications are pending analyst review &gt; 48hrs.</p>
                  </div>
                </li>
                <li className="flex gap-3 items-start">
                  <ShieldAlert size={16} className="text-blue-500 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-xs font-semibold text-gray-800 leading-tight">Compliance Update</p>
                    <p className="text-[10px] text-gray-500 mt-1">New KYC norms active. Ensure parameter update.</p>
                  </div>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="shadow-sm border-gray-200">
            <CardHeader className="py-2.5 px-4 border-b bg-gray-50/50">
              <span className="text-sm font-bold text-gray-800">Quick Actions</span>
            </CardHeader>
            <CardContent className="p-3 grid grid-cols-2 gap-2">
              <button className="bg-gray-50 border border-gray-200 hover:border-finsight-teal rounded text-xs p-2 text-center transition-colors">
                <FilePlus2 size={16} className="mx-auto mb-1 text-gray-500" />
                <span className="font-medium text-gray-700">New Run</span>
              </button>
              <button className="bg-gray-50 border border-gray-200 hover:border-finsight-teal rounded text-xs p-2 text-center transition-colors">
                <Users size={16} className="mx-auto mb-1 text-gray-500" />
                <span className="font-medium text-gray-700">Batch Upload</span>
              </button>
              <button className="bg-gray-50 border border-gray-200 hover:border-finsight-teal rounded text-xs p-2 text-center transition-colors">
                <FileText size={16} className="mx-auto mb-1 text-gray-500" />
                <span className="font-medium text-gray-700">MIS Report</span>
              </button>
              <button className="bg-gray-50 border border-gray-200 hover:border-finsight-teal rounded text-xs p-2 text-center transition-colors">
                <Briefcase size={16} className="mx-auto mb-1 text-gray-500" />
                <span className="font-medium text-gray-700">Portfolio</span>
              </button>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
