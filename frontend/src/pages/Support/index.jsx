import { Card, CardHeader, CardContent } from '../../components/common/Card';

const Support = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Help & Support</h1>
        <p className="text-gray-500">Get assistance and read documentation.</p>
      </div>

      <Card>
        <CardHeader>Coming Soon</CardHeader>
        <CardContent>
          <p className="text-gray-600">The Help & Support module is currently under development.</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Support;
