import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { submitAssessment } from '../../services/assessments';
import { FileUp, Loader2 } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

const NewAssessment = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [formData, setFormData] = useState({
    business_name: '',
    gstin: '',
    bank_account_number: '',
    ifsc_code: '',
  });

  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxSize: 10485760 // 10MB
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // Backend expects { msme_id }, use gstin as the MSME identifier
      const payload = { msme_id: formData.gstin || formData.business_name };
      const response = await submitAssessment(payload);
      navigate(`/assessment/${response.msme_id}`, { state: { result: response } });
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Assessment failed. Please try again.';
      setError(msg);
      console.error('Submission failed', err);
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

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      <Card>
        <CardHeader>Business Information</CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Business Name / MSME ID</label>
                <input 
                  required
                  type="text" 
                  name="business_name"
                  value={formData.business_name}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-finsight-teal focus:border-finsight-teal outline-none"
                  placeholder="e.g. raj_vendor" 
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
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-finsight-teal focus:border-finsight-teal outline-none"
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
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-finsight-teal focus:border-finsight-teal outline-none"
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
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-finsight-teal focus:border-finsight-teal outline-none"
                  placeholder="e.g. IBKL0000001" 
                />
              </div>
            </div>

            <div className="pt-4 border-t border-gray-100">
              <label className="block text-sm font-medium text-gray-700 mb-2">Upload Bank Statement (Optional)</label>
              <div {...getRootProps()} className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors ${isDragActive ? 'border-finsight-teal bg-finsight-teal/5' : 'border-gray-300 hover:bg-gray-50'}`}>
                <input {...getInputProps()} />
                <FileUp className={`${isDragActive ? 'text-finsight-teal' : 'text-gray-400'} mb-3`} size={32} />
                <p className="text-sm font-medium text-gray-700">
                  {file ? `Selected file: ${file.name}` : isDragActive ? "Drop the file here..." : "Click to upload or drag and drop"}
                </p>
                <p className="text-xs text-gray-500 mt-1">PDF, CSV, or XLSX up to 10MB</p>
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button 
                type="submit" 
                disabled={loading}
                className="bg-finsight-orange hover:bg-[#d66523] text-white px-6 py-2 rounded-md font-medium transition-colors flex items-center gap-2 disabled:opacity-70"
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
