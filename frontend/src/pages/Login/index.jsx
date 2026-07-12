import { useNavigate } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-lg border border-gray-200 w-full max-w-sm">
        <div className="flex justify-center mb-6 bg-finsight-darkTeal p-4 rounded-md">
          <img src="/finsight-logo.png" alt="FinSight Logo" className="h-10 object-contain" />
        </div>
        <h2 className="text-xl font-bold text-center text-gray-800 mb-2">Secure Authentication</h2>
        <p className="text-center text-gray-500 text-sm mb-6">Enter your enterprise credentials</p>
        
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Employee ID</label>
            <input type="text" className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-finsight-teal" defaultValue="EMP-4592" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input type="password" className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-finsight-teal" defaultValue="********" />
          </div>
        </div>

        <button 
          onClick={() => navigate('/dashboard')}
          className="w-full bg-finsight-teal text-white py-2 rounded-md hover:bg-finsight-darkTeal transition-colors font-medium shadow-sm"
        >
          Sign In
        </button>
      </div>
    </div>
  );
};

export default Login;
