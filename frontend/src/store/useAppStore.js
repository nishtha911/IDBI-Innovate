import { create } from 'zustand';

const useAppStore = create((set) => ({
  user: {
    name: 'Rahul Sharma',
    role: 'Relationship Manager',
    branch: 'Mumbai Main Branch',
  },
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));

export default useAppStore;
