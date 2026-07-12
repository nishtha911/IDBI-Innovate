import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../components/common/Card';
import { Search, Filter, ChevronRight, Check } from 'lucide-react';
import clsx from 'clsx';

const mockHistory = [
  { id: '10234', name: 'TechVision IT Solutions', date: 'Oct 24, 2026', score: 85, risk: 'Green' },
  { id: '10233', name: 'Metro Builders', date: 'Oct 22, 2026', score: 68, risk: 'Amber' },
  { id: '10232', name: 'GreenField Agri', date: 'Oct 18, 2026', score: 42, risk: 'Red' },
  { id: '10231', name: 'Sunrise Logistics', date: 'Oct 15, 2026', score: 79, risk: 'Green' },
  { id: '10230', name: 'Apex Manufacturing', date: 'Oct 10, 2026', score: 55, risk: 'Amber' },
];

const AssessmentHistory = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || '');
  const [filterRisk, setFilterRisk] = useState('All');
  const [showFilterDropdown, setShowFilterDropdown] = useState(false);

  useEffect(() => {
    const search = searchParams.get('search');
    if (search !== null) {
      setSearchTerm(search);
    }
  }, [searchParams]);

  const filteredHistory = mockHistory.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) || item.id.includes(searchTerm);
    const matchesRisk = filterRisk === 'All' || item.risk === filterRisk;
    return matchesSearch && matchesRisk;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Assessment History</h1>
        <p className="text-gray-500">View and search past financial assessments.</p>
      </div>

      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search by business name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-finsight-teal focus:border-finsight-teal outline-none"
            />
          </div>
          <div className="relative">
            <button 
              onClick={() => setShowFilterDropdown(!showFilterDropdown)}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Filter size={18} />
              {filterRisk === 'All' ? 'Filter' : `Risk: ${filterRisk}`}
            </button>
            {showFilterDropdown && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-md shadow-lg z-10 py-1">
                {['All', 'Green', 'Amber', 'Red'].map(risk => (
                  <button
                    key={risk}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center justify-between"
                    onClick={() => { setFilterRisk(risk); setShowFilterDropdown(false); }}
                  >
                    <span className={clsx(
                      risk === 'Green' ? 'text-green-600' :
                      risk === 'Amber' ? 'text-amber-600' :
                      risk === 'Red' ? 'text-red-600' : 'text-gray-700'
                    )}>{risk}</span>
                    {filterRisk === risk && <Check size={14} className="text-finsight-teal" />}
                  </button>
                ))}
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 text-gray-600 text-sm border-b border-gray-200">
                  <th className="px-6 py-3 font-medium">Assessment ID</th>
                  <th className="px-6 py-3 font-medium">Business Name</th>
                  <th className="px-6 py-3 font-medium">Date</th>
                  <th className="px-6 py-3 font-medium">Score</th>
                  <th className="px-6 py-3 font-medium">Risk Category</th>
                  <th className="px-6 py-3 font-medium"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredHistory.map((item) => (
                  <tr 
                    key={item.id} 
                    className="hover:bg-gray-50 transition-colors cursor-pointer group"
                    onClick={() => navigate(`/assessment/${item.id}`)}
                  >
                    <td className="px-6 py-4 text-sm font-medium text-finsight-teal">{item.id}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{item.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{item.date}</td>
                    <td className="px-6 py-4 text-sm font-medium">{item.score}</td>
                    <td className="px-6 py-4">
                      <span className={clsx(
                        "text-xs px-2.5 py-1 rounded-full font-medium",
                        item.risk === 'Green' ? 'bg-green-100 text-green-700' :
                        item.risk === 'Amber' ? 'bg-amber-100 text-amber-700' :
                        'bg-red-100 text-red-700'
                      )}>
                        {item.risk}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <ChevronRight size={18} className="text-gray-400 group-hover:text-finsight-teal transition-colors" />
                    </td>
                  </tr>
                ))}
                {filteredHistory.length === 0 && (
                  <tr>
                    <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                      No assessments found matching your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AssessmentHistory;
