import { Card, CardHeader, CardContent } from '../../components/common/Card';

const Analytics = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Analytics</h1>
        <p className="text-gray-500">View detailed analytics and portfolio metrics.</p>
      </div>

      <Card>
        <CardHeader>Coming Soon</CardHeader>
        <CardContent>
          <p className="text-gray-600">The Analytics module is currently under development.</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;
