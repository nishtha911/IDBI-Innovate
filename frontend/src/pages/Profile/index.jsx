import { Card, CardHeader, CardContent } from '../../components/common/Card';

const Profile = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Corporate Profile</h1>
        <p className="text-gray-500">Manage your corporate entity details and preferences.</p>
      </div>

      <Card>
        <CardHeader>Coming Soon</CardHeader>
        <CardContent>
          <p className="text-gray-600">The Corporate Profile module is currently under development.</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;
