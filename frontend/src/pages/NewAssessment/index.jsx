import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { submitAssessment } from '../../services/assessments';
import { FileUp, Loader2 } from 'lucide-react';

const NewAssessment = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    business_pan: '',
    gstin: '',
    bank_account_number: '',
    ifsc_code: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // In a real app, we'd send files too. The backend currently expects a JSON with PAN, GSTIN etc.
      // But based on our mocked backend, the endpoint is /score/evaluate taking bank_statement.
      // We will just mock the submit for now and redirect to a random id like /assessment/123
      // const response = await submitAssessment(formData);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      navigate(`/assessment/${Math.floor(Math.random() * 1000)}`);
    } catch (error) {
      console.error("Submission failed", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">New Financial Assessment</h1>
        <p className="text-gray-500">Enter business details to generate a health score.</p>
      </div>

      <Card>
        <CardHeader>Business Information</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Business PAN</label>
                <input 
                  required
                  type="text" 
                  name="business_pan"
                  value={formData.business_pan}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-idbi-teal focus:border-idbi-teal outline-none"
                  placeholder="e.g. ABCDE1234F" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">GSTIN</label>
                <input 
                  required
                  type="text" 
                  name="gstin"
                  value={formData.gstin}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-idbi-teal focus:border-idbi-teal outline-none"
                  placeholder="e.g. 27ABCDE1234F1Z5" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bank Account Number</label>
                <input 
                  required
                  type="text" 
                  name="bank_account_number"
                  value={formData.bank_account_number}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-idbi-teal focus:border-idbi-teal outline-none"
                  placeholder="e.g. 0123456789" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">IFSC Code</label>
                <input 
                  required
                  type="text" 
                  name="ifsc_code"
                  value={formData.ifsc_code}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-idbi-teal focus:border-idbi-teal outline-none"
                  placeholder="e.g. IBKL0000001" 
                />
              </div>
            </div>

            <div className="pt-4 border-t border-gray-100">
              <label className="block text-sm font-medium text-gray-700 mb-2">Upload Bank Statement (Optional)</label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-gray-50 transition-colors">
                <FileUp className="text-gray-400 mb-3" size={32} />
                <p className="text-sm font-medium text-gray-700">Click to upload or drag and drop</p>
                <p className="text-xs text-gray-500 mt-1">PDF, CSV, or XLSX up to 10MB</p>
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button 
                type="submit" 
                disabled={loading}
                className="bg-idbi-orange hover:bg-[#d66523] text-white px-6 py-2 rounded-md font-medium transition-colors flex items-center gap-2 disabled:opacity-70"
              >
                {loading && <Loader2 size={16} className="animate-spin" />}
                {loading ? 'Processing...' : 'Run Assessment'}
              </button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default NewAssessment;
