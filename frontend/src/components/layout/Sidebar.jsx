import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FilePlus2, History, Settings, LogOut } from 'lucide-react';
import useAppStore from '../../store/useAppStore';
import clsx from 'clsx';

const Sidebar = () => {
  const location = useLocation();
  const sidebarOpen = useAppStore((state) => state.sidebarOpen);

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'New Assessment', path: '/assessment/new', icon: FilePlus2 },
    { name: 'History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside
      className={clsx(
        'bg-idbi-teal text-white transition-all duration-300 flex flex-col',
        sidebarOpen ? 'w-64' : 'w-20'
      )}
    >
      <div className="h-16 flex items-center justify-center border-b border-idbi-darkTeal">
        <h1 className="text-xl font-bold font-sans tracking-wide">
          {sidebarOpen ? 'IDBI Innovate' : 'IDBI'}
        </h1>
      </div>
      
      <nav className="flex-1 py-6 flex flex-col gap-2 px-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname.startsWith(item.path);
          
          return (
            <Link
              key={item.name}
              to={item.path}
              className={clsx(
                'flex items-center gap-3 px-3 py-3 rounded-md transition-colors',
                isActive 
                  ? 'bg-idbi-orange text-white' 
                  : 'hover:bg-idbi-darkTeal text-gray-200'
              )}
              title={!sidebarOpen ? item.name : undefined}
            >
              <Icon size={20} className="shrink-0" />
              {sidebarOpen && <span className="font-medium">{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-idbi-darkTeal">
        <button className="flex items-center gap-3 px-3 py-2 w-full text-left text-gray-200 hover:text-white hover:bg-idbi-darkTeal rounded-md transition-colors">
          <LogOut size={20} className="shrink-0" />
          {sidebarOpen && <span className="font-medium">Logout</span>}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
