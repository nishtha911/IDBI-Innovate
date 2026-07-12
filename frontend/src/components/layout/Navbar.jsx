import { Menu, Bell, UserCircle, Search, Globe, ChevronDown, Phone, Mail } from 'lucide-react';
import useAppStore from '../../store/useAppStore';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import clsx from 'clsx';

const Navbar = () => {
  const toggleSidebar = useAppStore((state) => state.toggleSidebar);
  const user = useAppStore((state) => state.user);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('Corporate');
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const navigate = useNavigate();

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/history?search=${encodeURIComponent(searchQuery)}`);
      setSearchQuery('');
    }
  };

  return (
    <div className="flex flex-col w-full sticky top-0 z-10 shadow-sm">
      {/* Top Utility Bar (Very Dense) */}
      <div className="h-8 bg-finsight-darkTeal text-white text-xs flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          {['Personal', 'Corporate', 'NRI', 'Investor Relations'].map((tab) => (
            <span 
              key={tab} 
              onClick={() => setActiveTab(tab)}
              className={clsx(
                "cursor-pointer transition-colors flex items-center gap-2",
                activeTab === tab ? "text-finsight-orange font-semibold" : "hover:text-finsight-orange text-gray-300"
              )}
            >
              {tab}
            </span>
          ))}
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

        <div className="flex items-center gap-4 relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors relative"
          >
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-finsight-orange rounded-full"></span>
          </button>
          
          {showNotifications && (
            <div className="absolute top-12 right-12 w-64 bg-white border border-gray-200 shadow-lg rounded-md py-2 z-20">
              <p className="px-4 py-2 text-xs font-semibold border-b border-gray-100">Notifications</p>
              <div className="px-4 py-3 text-sm text-gray-600 border-b border-gray-100 hover:bg-gray-50 cursor-pointer">
                <p className="font-medium text-gray-800">API Alert</p>
                <p className="text-xs">GSTIN latency &gt; 2s</p>
              </div>
              <div className="px-4 py-3 text-sm text-gray-600 hover:bg-gray-50 cursor-pointer">
                <p className="font-medium text-gray-800">New Report</p>
                <p className="text-xs">Assessment 10234 is ready</p>
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-3 border-l border-gray-200 pl-4 relative">
            <div className="text-right hidden sm:block leading-tight">
              <p className="text-sm font-semibold text-gray-800">{user.name}</p>
              <p className="text-[10px] uppercase font-bold tracking-wider text-finsight-teal">{user.role}</p>
            </div>
            <UserCircle 
              size={32} 
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="text-gray-400 cursor-pointer hover:text-finsight-teal transition-colors" 
            />
            {showProfileMenu && (
              <div className="absolute top-10 right-0 w-48 bg-white border border-gray-200 shadow-lg rounded-md py-1 z-20">
                <div className="px-4 py-2 border-b border-gray-100">
                  <p className="text-sm font-semibold text-gray-800">{user.name}</p>
                  <p className="text-xs text-gray-500">{user.email || 'user@idbi.com'}</p>
                </div>
                <button onClick={() => { setShowProfileMenu(false); navigate('/profile'); }} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Profile</button>
                <button onClick={() => { setShowProfileMenu(false); navigate('/settings'); }} className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Settings</button>
                <button onClick={() => { setShowProfileMenu(false); navigate('/login'); }} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50">Logout</button>
              </div>
            )}
          </div>
        </div>
      </header>
    </div>
  );
};

export default Navbar;
