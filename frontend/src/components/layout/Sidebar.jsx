import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FilePlus2, History, Settings, LogOut, FileText, HelpCircle, BarChart3, Briefcase } from 'lucide-react';
import useAppStore from '../../store/useAppStore';
import clsx from 'clsx';

const Sidebar = () => {
  const location = useLocation();
  const sidebarOpen = useAppStore((state) => state.sidebarOpen);

  const mainNavItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'New Assessment', path: '/assessment/new', icon: FilePlus2 },
    { name: 'History', path: '/history', icon: History },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  ];
  
  const secondaryNavItems = [
    { name: 'Corporate Profile', path: '/profile', icon: Briefcase },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'Help & Support', path: '/support', icon: HelpCircle },
  ];

  return (
    <aside
      className={clsx(
        'bg-finsight-teal text-white transition-all duration-300 flex flex-col shadow-lg z-20',
        sidebarOpen ? 'w-64' : 'w-20'
      )}
    >
      <div className="h-16 flex items-center justify-center border-b border-finsight-darkTeal shrink-0">
        {sidebarOpen ? (
          <img src="/finsight-logo.png" alt="FinSight Logo" className="h-10 object-contain" />
        ) : (
          <img src="/finsight-logo.png" alt="FS" className="h-8 object-contain" />
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto overflow-x-hidden flex flex-col gap-6 py-6 custom-scrollbar">
        
        {/* Main Navigation */}
        <nav className="flex flex-col gap-1 px-3">
          {sidebarOpen && <p className="text-[10px] uppercase font-bold text-finsight-lightTeal/60 px-3 mb-2 tracking-wider">Main Menu</p>}
          {mainNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);
            
            return (
              <Link
                key={item.name}
                to={item.path}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm',
                  isActive 
                    ? 'bg-finsight-orange text-white font-semibold shadow-sm' 
                    : 'hover:bg-finsight-darkTeal text-gray-200 hover:text-white'
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <Icon size={18} className="shrink-0" />
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Secondary Navigation */}
        <nav className="flex flex-col gap-1 px-3">
          {sidebarOpen && <p className="text-[10px] uppercase font-bold text-finsight-lightTeal/60 px-3 mb-2 tracking-wider">Administration</p>}
          {secondaryNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);
            
            return (
              <Link
                key={item.name}
                to={item.path}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm',
                  isActive 
                    ? 'bg-finsight-orange text-white font-semibold shadow-sm' 
                    : 'hover:bg-finsight-darkTeal text-gray-200 hover:text-white'
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <Icon size={18} className="shrink-0" />
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

      </div>

      <div className="p-4 border-t border-finsight-darkTeal shrink-0">
        {sidebarOpen && (
          <div className="mb-4 p-3 bg-finsight-darkTeal rounded-lg text-xs">
            <p className="font-semibold mb-1">System Status</p>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              <span className="text-gray-300">All services operational</span>
            </div>
          </div>
        )}
        <button className="flex items-center gap-3 px-3 py-2 w-full text-left text-gray-200 hover:text-white hover:bg-finsight-darkTeal rounded-md transition-colors text-sm">
          <LogOut size={18} className="shrink-0 text-finsight-orange" />
          {sidebarOpen && <span className="font-medium">Secure Logout</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
