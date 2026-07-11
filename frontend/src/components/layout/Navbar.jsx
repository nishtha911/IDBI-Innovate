import { Menu, Bell, UserCircle } from 'lucide-react';
import useAppStore from '../../store/useAppStore';

const Navbar = () => {
  const toggleSidebar = useAppStore((state) => state.toggleSidebar);
  const user = useAppStore((state) => state.user);

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleSidebar}
          className="p-2 text-gray-500 hover:bg-gray-100 rounded-md transition-colors"
        >
          <Menu size={20} />
        </button>
        <div className="hidden sm:block">
          <h2 className="text-lg font-semibold text-gray-800">MSME Financial Health Card</h2>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors relative">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-idbi-orange rounded-full"></span>
        </button>
        
        <div className="flex items-center gap-3 border-l border-gray-200 pl-4">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-gray-800">{user.name}</p>
            <p className="text-xs text-gray-500">{user.role}</p>
          </div>
          <UserCircle size={32} className="text-gray-400" />
        </div>
      </div>
    </header>
  );
};

export default Navbar;
