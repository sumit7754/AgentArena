import React, { useEffect, useState } from 'react';
import HomeLayout from '../Layouts/HomeLayout';
import PlaygroundHealthCheck from '../components/PlaygroundHealthCheck';
import { FiUsers, FiFileText, FiSettings, FiActivity, FiCpu, FiTrendingUp, FiTarget, FiZap } from 'react-icons/fi';
import axiosInstance from '../Helper/axiosInstance';
import toast from 'react-hot-toast';

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    total_agents: 0,
    total_tasks: 0,
    total_submissions: 0,
    completed_submissions: 0,
    avg_score: 0,
    success_rate: 0,
    recent_activity: []
  });

  const [tasks, setTasks] = useState([]);
  const [analytics, setAnalytics] = useState({
    avgPerformance: 0,
    totalBenchmarks: 0,
    activeAgents: 0,
    weeklyGrowth: 0
  });

  // Fetch data when component mounts
  useEffect(() => {
    fetchAdminStats();
    fetchTasks();
  }, []);

  // Fetch admin stats from API
  const fetchAdminStats = async () => {
    try {
      const response = await axiosInstance.get('/admin/stats');
      setStats(response.data);
      // Update analytics with data from stats
      setAnalytics({
        avgPerformance: response.data.avg_score || 0,
        totalBenchmarks: response.data.total_submissions || 0,
        activeAgents: response.data.total_agents || 0,
        weeklyGrowth: 0
      });
    } catch (error) {
      toast.error('Failed to load admin dashboard stats');
      console.error('Error fetching admin stats:', error);
    }
  };

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      const response = await axiosInstance.get('/tasks');
      setTasks(response.data || []);
    } catch (error) {
      toast.error('Failed to load tasks');
      console.error('Error fetching tasks:', error);
    }
  };

  return (
    <HomeLayout>
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold text-cyan-500 mb-8">Admin Command Center</h1>
        <p className="text-lg text-cyan-700 mb-8">AI Agent Benchmarking Platform Analytics</p>

        {/* Stats Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg shadow-lg p-6 border border-slate-700">
            <div className="flex items-center mb-4">
              <div className="p-3 rounded-full bg-slate-700 text-blue-400">
                <FiUsers size={24} />
              </div>
              <div className="ml-4">
                <h3 className="text-gray-400 text-sm">Total Users</h3>
                <p className="text-4xl text-cyan-400 font-bold">{stats.total_users || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg shadow-lg p-6 border border-slate-700">
            <div className="flex items-center mb-4">
              <div className="p-3 rounded-full bg-slate-700 text-purple-400">
                <FiCpu size={24} />
              </div>
              <div className="ml-4">
                <h3 className="text-gray-400 text-sm">Active Agents</h3>
                <p className="text-4xl text-purple-400 font-bold">{stats.total_agents || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg shadow-lg p-6 border border-slate-700">
            <div className="flex items-center mb-4">
              <div className="p-3 rounded-full bg-slate-700 text-green-400">
                <FiTarget size={24} />
              </div>
              <div className="ml-4">
                <h3 className="text-gray-400 text-sm">Benchmarks Run</h3>
                <p className="text-4xl text-green-400 font-bold">{stats.total_submissions || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg shadow-lg p-6 border border-slate-700">
            <div className="flex items-center mb-4">
              <div className="p-3 rounded-full bg-slate-700 text-yellow-400">
                <FiTrendingUp size={24} />
              </div>
              <div className="ml-4">
                <h3 className="text-gray-400 text-sm">Avg Performance</h3>
                <p className="text-4xl text-yellow-400 font-bold">{stats.avg_score || 0}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-700 mb-8">
          <button 
            className={`mr-4 py-2 px-4 ${activeTab === 'overview' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400'}`}
            onClick={() => setActiveTab('overview')}
          >
            <FiActivity className="inline mr-2" />Platform Analytics
          </button>
          <button 
            className={`mr-4 py-2 px-4 ${activeTab === 'tasks' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400'}`}
            onClick={() => setActiveTab('tasks')}
          >
            <FiFileText className="inline mr-2" />Task Management
          </button>
          <button 
            className={`mr-4 py-2 px-4 ${activeTab === 'users' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400'}`}
            onClick={() => setActiveTab('users')}
          >
            <FiUsers className="inline mr-2" />User Management
          </button>
          <button 
            className={`py-2 px-4 ${activeTab === 'system' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-400'}`}
            onClick={() => setActiveTab('system')}
          >
            <FiSettings className="inline mr-2" />System Health
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div>
            <div className="flex items-center mb-6">
              <FiZap className="mr-2 text-cyan-500" size={24} />
              <h2 className="text-xl font-bold text-white">Platform Performance Analytics</h2>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Top Performing Agents */}
              <div className="bg-slate-800 rounded-lg shadow-lg p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Top Performing Agents</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full bg-slate-900 rounded-lg">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Agent</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Score</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Tasks</th>
                      </tr>
                    </thead>
                    <tbody>
                      {/* No real data available yet, will show placeholder or empty state */}
                      <tr className="border-b border-slate-800">
                        <td className="px-4 py-4 text-sm text-gray-300" colSpan="3">
                          No agent performance data available yet
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              {/* Performance Trend */}
              <div className="bg-slate-800 rounded-lg shadow-lg p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Performance Trend</h3>
                <div className="grid grid-cols-7 gap-1 h-48">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => (
                    <div key={day} className="flex flex-col items-center">
                      <div className="flex-grow w-full bg-blue-500 opacity-40 rounded-t-md"></div>
                      <span className="text-xs text-gray-400 mt-2">{day}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Recent Platform Activity */}
            <div className="mt-8 bg-slate-800 rounded-lg shadow-lg p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Platform Activity</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-slate-900 rounded-lg">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Activity</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">User</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Task</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.recent_activity && stats.recent_activity.length > 0 ? (
                      stats.recent_activity.map((activity, idx) => (
                        <tr key={activity.id || idx} className="border-b border-slate-800">
                          <td className="px-4 py-4 text-sm text-blue-400">{activity.type}</td>
                          <td className="px-4 py-4 text-sm text-gray-300">{activity.user}</td>
                          <td className="px-4 py-4 text-sm text-gray-300">{activity.task}</td>
                          <td className="px-4 py-4 text-sm text-gray-300">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              activity.status === 'COMPLETED' ? 'bg-green-900 text-green-300' : 
                              activity.status === 'FAILED' ? 'bg-red-900 text-red-300' : 
                              'bg-yellow-900 text-yellow-300'
                            }`}>
                              {activity.status}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-400">
                            {activity.timestamp ? new Date(activity.timestamp).toLocaleString() : 'N/A'}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="px-4 py-4 text-sm text-gray-400 text-center">
                          No recent activity found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'tasks' && (
          <div>
            <div className="flex items-center mb-6">
              <FiFileText className="mr-2 text-cyan-500" size={24} />
              <h2 className="text-xl font-bold text-white">Task Management</h2>
            </div>
            
            <div className="bg-slate-800 rounded-lg shadow-lg p-6 border border-slate-700">
              <div className="mb-4 flex justify-between items-center">
                <h3 className="text-lg font-semibold text-white">All Tasks</h3>
                <button className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded">
                  Create Task
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-slate-900 rounded-lg">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Title</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Difficulty</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Environment</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Submissions</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.length > 0 ? tasks.map(task => (
                      <tr key={task.id} className="border-b border-slate-800">
                        <td className="px-4 py-4 text-sm text-gray-300">{task.title}</td>
                        <td className="px-4 py-4 text-sm">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            task.difficulty === 'EASY' ? 'bg-green-900 text-green-300' : 
                            task.difficulty === 'MEDIUM' ? 'bg-yellow-900 text-yellow-300' : 
                            'bg-red-900 text-red-300'
                          }`}>
                            {task.difficulty}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-sm text-gray-300">{task.webArenaEnvironment || 'Not specified'}</td>
                        <td className="px-4 py-4 text-sm text-gray-300">{task.submissionCount || 0}</td>
                        <td className="px-4 py-4 text-sm text-gray-300">
                          <button className="text-blue-400 hover:text-blue-300 mr-2">Edit</button>
                          <button className="text-red-400 hover:text-red-300">Delete</button>
                        </td>
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan="5" className="px-4 py-4 text-sm text-gray-400 text-center">
                          No tasks found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'users' && (
          <div>
            <div className="flex items-center mb-6">
              <FiUsers className="mr-2 text-cyan-500" size={24} />
              <h2 className="text-xl font-bold text-white">User Management</h2>
            </div>
            
            <div className="bg-slate-800 rounded-lg shadow-lg p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4">All Users</h3>
              <p className="text-gray-400 mb-4">
                User management functionality requires a dedicated API endpoint to be implemented.
              </p>
            </div>
          </div>
        )}
        
        {activeTab === 'system' && (
          <div>
            <div className="flex items-center mb-6">
              <FiSettings className="mr-2 text-cyan-500" size={24} />
              <h2 className="text-xl font-bold text-white">System Health</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-slate-800 rounded-lg shadow-lg p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Playground Status</h3>
                <PlaygroundHealthCheck />
              </div>
              
              <div className="bg-slate-800 rounded-lg shadow-lg p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">API Health</h3>
                <div className="p-4 bg-green-900 bg-opacity-20 border border-green-700 rounded-lg">
                  <div className="flex items-center">
                    <div className="h-3 w-3 rounded-full bg-green-500 mr-2 animate-pulse"></div>
                    <span className="text-green-400">API Server operational</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </HomeLayout>
  );
}

export default AdminDashboard;
