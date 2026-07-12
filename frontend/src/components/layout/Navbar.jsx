import { Menu, Bell, UserCircle, Search, Globe, ChevronDown, Phone, Mail } from 'lucide-react';
import useAppStore from '../../store/useAppStore';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const toggleSidebar = useAppStore((state) => state.toggleSidebar);
  const user = useAppStore((state) => state.user);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate('/history');
      setSearchQuery('');
    }
  };

  return (
    <div className="flex flex-col w-full sticky top-0 z-10 shadow-sm">
      {/* Top Utility Bar (Very Dense) */}
      <div className="h-8 bg-finsight-darkTeal text-white text-xs flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <span className="hover:text-finsight-orange cursor-pointer transition-colors">Personal</span>
          <span className="text-gray-400">|</span>
          <span className="hover:text-finsight-orange cursor-pointer transition-colors font-semibold">Corporate</span>
          <span className="text-gray-400">|</span>
          <span className="hover:text-finsight-orange cursor-pointer transition-colors">NRI</span>
          <span className="text-gray-400">|</span>
          <span className="hover:text-finsight-orange cursor-pointer transition-colors">Investor Relations</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1 hover:text-finsight-orange cursor-pointer transition-colors">
            <Phone size={12} />
            <span>1800-FIN-SIGHT</span>
          </div>
          <div className="flex items-center gap-1 hover:text-finsight-orange cursor-pointer transition-colors">
            <Mail size={12} />
            <span>corporate@finsight.com</span>
          </div>
          <div className="flex items-center gap-1 border-l border-gray-500 pl-4 hover:text-finsight-orange cursor-pointer transition-colors">
            <Globe size={12} />
            <span>English</span>
            <ChevronDown size={12} />
          </div>
        </div>
      </div>

      {/* Main Header Area */}
      <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <button 
            onClick={toggleSidebar}
            className="p-2 text-gray-500 hover:bg-gray-100 rounded-md transition-colors"
          >
            <Menu size={20} />
          </button>
          <div className="hidden sm:block">
            <h2 className="text-xl font-bold text-gray-800 tracking-tight">FinSight <span className="font-normal text-finsight-teal text-lg">Enterprise Assessment</span></h2>
          </div>
        </div>

        {/* Global Search */}
        <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
          <form onSubmit={handleSearchSubmit} className="relative w-full">
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search companies, GSTIN, or reports..." 
              className="w-full pl-10 pr-4 py-1.5 bg-gray-50 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-finsight-teal focus:border-finsight-teal"
            />
            <Search size={16} className="absolute left-3 top-2 text-gray-400" />
          </form>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors relative">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-finsight-orange rounded-full"></span>
          </button>
          
          <div className="flex items-center gap-3 border-l border-gray-200 pl-4">
            <div className="text-right hidden sm:block leading-tight">
              <p className="text-sm font-semibold text-gray-800">{user.name}</p>
              <p className="text-[10px] uppercase font-bold tracking-wider text-finsight-teal">{user.role}</p>
            </div>
            <UserCircle size={32} className="text-gray-400 cursor-pointer hover:text-finsight-teal transition-colors" />
          </div>
        </div>
      </header>
    </div>
  );
};

export default Navbar;
