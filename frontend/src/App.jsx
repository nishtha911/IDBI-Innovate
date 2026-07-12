import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import NewAssessment from './pages/NewAssessment';
import AssessmentResult from './pages/AssessmentResult';
import AssessmentHistory from './pages/AssessmentHistory';
import Settings from './pages/Settings';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';
import Reports from './pages/Reports';
import Support from './pages/Support';
import Login from './pages/Login';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="assessment/new" element={<NewAssessment />} />
          <Route path="assessment/:id" element={<AssessmentResult />} />
          <Route path="history" element={<AssessmentHistory />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="profile" element={<Profile />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
          <Route path="support" element={<Support />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
