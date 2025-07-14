import './App.css';
import { Route, Routes } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Pages
import HomePage from './Pages/HomePage';
import Dashboard from './Pages/Dashboard';
import Signup from './Pages/Signup';
import Login from './Pages/Login';
import Tasks from './Pages/Tasks';
import TaskDetails from './Pages/TaskDetails';
import Agents from './Pages/Agents';
import CreateAgent from './Pages/CreateAgent';
import AgentDetails from './Pages/AgentDetails';
import Submissions from './Pages/Submissions';
import SubmissionDetails from './Pages/SubmissionDetails';
import UserProfile from './Pages/UserProfile';
import Leaderboard from './Pages/Leaderboard';
import TaskLeaderboard from './Pages/TaskLeaderboard';
import AdminDashboard from './Pages/AdminDashboard';
import DisplayAgents from './Pages/DisplayAgents';
import Playground from './Pages/Playground';
import NotFound from './Pages/NotFound';

// Auth Context
import { AuthProvider } from './contexts/AuthContext';

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/login" element={<Login />} />
      <Route path="/leaderboard" element={<Leaderboard />} />

      {/* Unprotected Internal Routes */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/playground" element={<Playground />} />
      <Route path="/tasks" element={<Tasks />} />
      <Route path="/tasks/:taskId" element={<TaskDetails />} />
      <Route path="/submissions" element={<Submissions />} />
      <Route path="/submissions/:submissionId" element={<SubmissionDetails />} />
      <Route path="/agents" element={<DisplayAgents />} />
      <Route path="/agents/create" element={<CreateAgent />} />
      <Route path="/agents/:agentId" element={<AgentDetails />} />
      <Route path="/leaderboard/task/:taskId" element={<TaskLeaderboard />} />
      <Route path="/profile" element={<UserProfile />} />
      <Route path="/admin/dashboard" element={<AdminDashboard />} />

      {/* 404 Fallback */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <AppRoutes />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1f2937',
              color: '#ffffff',
              border: '1px solid #374151',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#ffffff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#ffffff',
              },
            },
          }}
        />
      </div>
    </AuthProvider>
  );
}

export default App;
