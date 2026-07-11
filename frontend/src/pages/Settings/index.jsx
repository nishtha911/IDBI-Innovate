import { Card, CardHeader, CardContent } from '../../components/common/Card';
import useAppStore from '../../store/useAppStore';

const Settings = () => {
  const user = useAppStore((state) => state.user);

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
        <p className="text-gray-500">Manage your profile and application preferences.</p>
      </div>

      <Card>
        <CardHeader>Profile Information</CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input 
                type="text" 
                defaultValue={user.name}
                className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
                disabled
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <input 
                type="text" 
                defaultValue={user.role}
                className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
                disabled
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Branch</label>
              <input 
                type="text" 
                defaultValue={user.branch}
                className="w-full px-4 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600"
                disabled
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>Preferences</CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-800">Email Notifications</h3>
              <p className="text-sm text-gray-500">Receive alerts when a new assessment is completed.</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-finsight-teal"></div>
            </label>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;
