import { useState, useEffect } from 'react';
import { Users, FileWarning, ShieldAlert, TrendingUp } from 'lucide-react';
import { MetricCard } from '../../components/common/MetricCard';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { getDashboardMetrics } from '../../services/assessments';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
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
    return <div className="flex items-center justify-center h-full">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-500">Overview of MSME financial assessments.</p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <MetricCard
          title="Total Assessments"
          value={metrics?.totalAssessments || 0}
          icon={Users}
          trend="up"
          trendLabel="12% from last month"
          colorClass="text-idbi-teal bg-idbi-lightTeal"
        />
        <MetricCard
          title="Avg. Health Score"
          value={metrics?.avgScore || 0}
          icon={TrendingUp}
          trend="up"
          trendLabel="3 points"
          colorClass="text-blue-600 bg-blue-50"
        />
        <MetricCard
          title="High Risk Profiles"
          value={metrics?.highRisk || 0}
          icon={ShieldAlert}
          trend="down"
          trendLabel="5% decrease"
          colorClass="text-red-600 bg-red-50"
        />
        <MetricCard
          title="Pending Reviews"
          value="4"
          icon={FileWarning}
          colorClass="text-idbi-orange bg-orange-50"
        />
      </div>

      {/* Charts & Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <Card className="col-span-2">
          <CardHeader>Average Health Score Trend</CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics?.recentTrends || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#6B7280' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6B7280' }} domain={['dataMin - 10', 'dataMax + 10']} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#008479" 
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#008479', strokeWidth: 2, stroke: '#fff' }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Quick Actions / Recent Activity */}
        <Card>
          <CardHeader>Recent Activity</CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: 'TechVision IT Solutions', score: 85, status: 'Approved' },
                { name: 'GreenField Agri', score: 42, status: 'Rejected' },
                { name: 'Metro Builders', score: 68, status: 'Under Review' },
              ].map((item, idx) => (
                <div key={idx} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="font-medium text-gray-800">{item.name}</p>
                    <p className="text-sm text-gray-500">Score: {item.score}</p>
                  </div>
                  <span className={clsx(
                    "text-xs px-2 py-1 rounded-full font-medium",
                    item.status === 'Approved' ? 'bg-green-100 text-green-700' :
                    item.status === 'Rejected' ? 'bg-red-100 text-red-700' :
                    'bg-yellow-100 text-yellow-700'
                  )}>
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
