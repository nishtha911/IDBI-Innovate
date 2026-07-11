import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import { Shield } from 'lucide-react';

const MainLayout = () => {
  return (
    <div className="flex h-screen bg-finsight-beige overflow-hidden font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto">
          {/* Dense Main Area with Breadcrumbs and Sub-header could go here */}
          <div className="min-h-full flex flex-col">
            <div className="flex-1 p-6 max-w-7xl mx-auto w-full">
              <Outlet />
            </div>
            
            {/* Corporate Dense Footer */}
            <footer className="bg-white border-t border-gray-200 mt-auto py-8 px-6 text-sm text-gray-500 shrink-0">
              <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                <div>
                  <h4 className="font-semibold text-gray-800 mb-4 uppercase tracking-wider text-xs">About FinSight</h4>
                  <ul className="space-y-2 text-xs">
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Corporate Overview</a></li>
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Board of Directors</a></li>
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Careers</a></li>
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Contact Us</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-4 uppercase tracking-wider text-xs">Regulatory & Legal</h4>
                  <ul className="space-y-2 text-xs">
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Terms of Service</a></li>
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Privacy Policy</a></li>
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">RTI Act</a></li>
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Cyber Security Policy</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-4 uppercase tracking-wider text-xs">Investor Corner</h4>
                  <ul className="space-y-2 text-xs">
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Financial Results</a></li>
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Shareholding Pattern</a></li>
                    <li><a href="#" className="hover:text-finsight-teal transition-colors">Disclosures</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-4 uppercase tracking-wider text-xs">Secure Banking</h4>
                  <div className="flex items-start gap-2 bg-gray-50 p-3 rounded-md border border-gray-200">
                    <Shield size={16} className="text-finsight-teal shrink-0 mt-0.5" />
                    <p className="text-[10px] leading-relaxed">
                      FinSight will never ask for your password or OTP. Please be aware of phishing attempts. Report suspicious activity to our toll-free number immediately.
                    </p>
                  </div>
                </div>
              </div>
              <div className="border-t border-gray-100 pt-4 flex flex-col md:flex-row items-center justify-between text-[10px] text-gray-400">
                <p>&copy; {new Date().getFullYear()} FinSight Analytics Enterprise. All rights reserved.</p>
                <p>System Version: v4.12.0 (Stable) | Node: IND-M-04</p>
              </div>
            </footer>
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
