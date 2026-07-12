import { Card, CardHeader, CardContent } from '../../components/common/Card';

const Reports = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Reports</h1>
        <p className="text-gray-500">Generate and download custom financial reports.</p>
      </div>

      <Card>
        <CardHeader>Coming Soon</CardHeader>
        <CardContent>
          <p className="text-gray-600">The Reports module is currently under development.</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Reports;
