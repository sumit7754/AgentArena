import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiCpu, FiTarget, FiClipboard, FiAward, FiTrendingUp } from 'react-icons/fi';
import axiosInstance from '../Helper/axiosInstance';
import HomeLayout from '../Layouts/HomeLayout';
import { useAuth } from '../contexts/AuthContext';

function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    agents: 0,
    submissions: 0,
    completed_submissions: 0,
    available_tasks: 0,
    average_score: 0
  });
  const [recentActivity, setRecentActivity] = useState({
    submissions: [],
    agents: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axiosInstance.get('/admin/user/dashboard/stats');
        const data = response.data;
        
        setStats(data.user_stats);
        setRecentActivity(data.recent_activity);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <HomeLayout>
        <div className="min-h-[90vh] flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
        </div>
      </HomeLayout>
    );
  }

  return (
    <HomeLayout>
      <div className="min-h-[90vh] py-12 px-8 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="mb-12">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent mb-2">
              Welcome back, {user?.name || "User"}
            </h1>
            <p className="text-xl text-cyan-200">Your agent benchmarking dashboard</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300">
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center">
                  <FiCpu className="text-xl text-white" />
                </div>
                <span className="text-3xl font-bold text-cyan-400">{stats.agents}</span>
              </div>
              <h3 className="text-lg font-semibold text-cyan-100">Your Agents</h3>
              <p className="text-sm text-cyan-300 mt-1">Active AI agents</p>
              <Link to="/agents" className="text-sm text-cyan-400 hover:text-cyan-300 mt-4 inline-block">
                Manage agents →
              </Link>
            </div>

            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300">
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                  <FiClipboard className="text-xl text-white" />
                </div>
                <span className="text-3xl font-bold text-green-400">{stats.submissions}</span>
              </div>
              <h3 className="text-lg font-semibold text-cyan-100">Submissions</h3>
              <p className="text-sm text-cyan-300 mt-1">Agent benchmark tests</p>
              <Link to="/submissions" className="text-sm text-green-400 hover:text-green-300 mt-4 inline-block">
                View submissions →
              </Link>
            </div>

            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300">
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
                  <FiTarget className="text-xl text-white" />
                </div>
                <span className="text-3xl font-bold text-yellow-400">{stats.available_tasks}</span>
              </div>
              <h3 className="text-lg font-semibold text-cyan-100">Available Tasks</h3>
              <p className="text-sm text-cyan-300 mt-1">Benchmark challenges</p>
              <Link to="/tasks" className="text-sm text-yellow-400 hover:text-yellow-300 mt-4 inline-block">
                Explore tasks →
              </Link>
            </div>

            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300">
              <div className="flex justify-between items-start mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl flex items-center justify-center">
                  <FiAward className="text-xl text-white" />
                </div>
                <span className="text-3xl font-bold text-purple-400">{stats.average_score}%</span>
              </div>
              <h3 className="text-lg font-semibold text-cyan-100">Average Score</h3>
              <p className="text-sm text-cyan-300 mt-1">Performance rating</p>
              <Link to="/leaderboard" className="text-sm text-purple-400 hover:text-purple-300 mt-4 inline-block">
                View leaderboard →
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20">
              <h3 className="text-xl font-bold text-cyan-100 mb-6">Recent Activity</h3>
              <div className="space-y-6">
                {recentActivity.submissions.length > 0 || recentActivity.agents.length > 0 ? (
                  <>
                    {recentActivity.submissions.slice(0, 3).map((submission, index) => (
                      <div key={submission.id} className="flex gap-4 border-l-2 border-green-500 pl-4 py-2">
                        <div className="flex-1">
                          <div className="flex justify-between">
                            <h4 className="font-semibold text-cyan-200">
                              Submission: {submission.task_name}
                            </h4>
                            <span className="text-xs text-gray-400">
                              {new Date(submission.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400">
                            Status: {submission.status} {submission.score ? `- Score: ${submission.score}%` : ''}
                          </p>
                        </div>
                      </div>
                    ))}
                    {recentActivity.agents.slice(0, 2).map((agent, index) => (
                      <div key={agent.id} className="flex gap-4 border-l-2 border-cyan-500 pl-4 py-2">
                        <div className="flex-1">
                          <div className="flex justify-between">
                            <h4 className="font-semibold text-cyan-200">
                              Agent "{agent.name}" created
                            </h4>
                            <span className="text-xs text-gray-400">
                              {new Date(agent.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400">
                            Type: {agent.agent_type}
                          </p>
                        </div>
                      </div>
                    ))}
                  </>
                ) : (
                  <p className="text-gray-400">No recent activity. Start by creating an agent or submitting a task!</p>
                )}
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20">
              <h3 className="text-xl font-bold text-cyan-100 mb-6">Quick Actions</h3>
              <div className="space-y-4">
                <Link 
                  to="/agents/create" 
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 hover:from-cyan-600 hover:to-blue-700 transition-colors"
                >
                  <FiCpu /> Create New Agent
                </Link>
                <Link 
                  to="/tasks" 
                  className="w-full bg-gradient-to-r from-yellow-500 to-orange-600 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 hover:from-yellow-600 hover:to-orange-700 transition-colors"
                >
                  <FiTarget /> Browse Tasks
                </Link>
                <Link 
                  to="/playground" 
                  className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 hover:from-green-600 hover:to-emerald-700 transition-colors"
                >
                  <FiTrendingUp /> Test in Playground
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </HomeLayout>
  );
}

export default Dashboard; 