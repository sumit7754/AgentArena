import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiUser, FiActivity, FiCpu, FiTarget, FiClock, FiTrendingUp, FiZap, FiAward, FiBarChart } from 'react-icons/fi';
import axiosInstance from '../Helper/axiosInstance';
import HomeLayout from '../Layouts/HomeLayout';
import toast from 'react-hot-toast';

function UserProfile() {
  const [user, setUser] = useState(null);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [analytics, setAnalytics] = useState({
    totalTests: 0,
    avgScore: 0,
    bestScore: 0,
    totalRuntime: 0,
    efficiency: 0,
    reliability: 0
  });

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      
      // Get user profile analytics
      const analyticsResponse = await axiosInstance.get('/admin/user/profile/analytics');
      setAnalytics(analyticsResponse.data || {});
      
      // Get agents
      const agentsResponse = await axiosInstance.get('/agents');
      setAgents(agentsResponse.data || []);
      
      // Get user profile
      const userData = {
        name: localStorage.getItem('username') || 'AI Researcher',
        email: localStorage.getItem('email') || 'user@example.com',
        role: localStorage.getItem('role') || 'USER'
      };
      setUser(userData);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching user data:', error);
      toast.error('Failed to load profile data');
      setLoading(false);
    }
  };

  const getAgentMetrics = (agent) => {
    // Try to get metrics from agent data first
    if (agent.metrics) {
      return agent.metrics;
    }
    
    // Fall back to defaults if no real metrics available
    return {
      testsRun: 5,
      avgScore: 75,
      lastRun: 'N/A',
      trend: 'neutral'
    };
  };

  if (loading) {
    return (
      <HomeLayout>
        <div className="min-h-[90vh] pt-12 px-8 flex flex-col items-center justify-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mb-4"></div>
          <p className="text-cyan-200">Loading profile...</p>
        </div>
      </HomeLayout>
    );
  }

  return (
    <HomeLayout>
      <div className="min-h-[90vh] pt-12 px-8 text-white bg-gradient-to-br from-gray-900 via-blue-900/20 to-cyan-900/20">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-r from-cyan-500/10 to-blue-600/10 backdrop-blur-lg rounded-2xl p-8 mb-12 border border-cyan-500/20 shadow-2xl">
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
                <FiUser className="text-3xl text-white" />
              </div>
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-cyan-100 mb-2">{user?.name}</h1>
                <p className="text-cyan-300 text-lg mb-3">{user?.email}</p>
                <div className="flex items-center gap-4">
                  <span className="inline-block px-3 py-1 bg-cyan-500/20 text-cyan-300 text-sm rounded-full font-semibold">
                    {user?.role}
                  </span>
                  <div className="flex items-center gap-2 text-sm text-green-400">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span>Active</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-cyan-400">{agents.length}</div>
                <div className="text-sm text-cyan-300">Agents Created</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300">
              <div className="flex items-center gap-3 mb-3">
                <FiActivity className="text-cyan-400 text-2xl" />
                <h3 className="font-bold text-cyan-100">Total Tests</h3>
              </div>
              <div className="text-3xl font-bold text-cyan-400 mb-1">{analytics.totalTests}</div>
              <div className="text-sm text-cyan-300">Benchmarks completed</div>
            </div>

            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300">
              <div className="flex items-center gap-3 mb-3">
                <FiTarget className="text-green-400 text-2xl" />
                <h3 className="font-bold text-cyan-100">Average Score</h3>
              </div>
              <div className="text-3xl font-bold text-green-400 mb-1">{analytics.avgScore}%</div>
              <div className="text-sm text-cyan-300">Across all agents</div>
            </div>

            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300">
              <div className="flex items-center gap-3 mb-3">
                <FiAward className="text-yellow-400 text-2xl" />
                <h3 className="font-bold text-cyan-100">Best Score</h3>
              </div>
              <div className="text-3xl font-bold text-yellow-400 mb-1">{analytics.bestScore}%</div>
              <div className="text-sm text-cyan-300">Personal record</div>
            </div>

            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300">
              <div className="flex items-center gap-3 mb-3">
                <FiClock className="text-blue-400 text-2xl" />
                <h3 className="font-bold text-cyan-100">Runtime</h3>
              </div>
              <div className="text-3xl font-bold text-blue-400 mb-1">{analytics.totalRuntime}h</div>
              <div className="text-sm text-cyan-300">Total execution time</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg rounded-2xl border border-cyan-500/20 shadow-2xl">
            <div className="border-b border-gray-700/50">
              <div className="flex">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`px-8 py-4 font-bold transition-all duration-300 ${
                    activeTab === 'overview' 
                      ? 'text-cyan-400 border-b-2 border-cyan-400 bg-cyan-400/5' 
                      : 'text-gray-400 hover:text-cyan-300'
                  }`}
                >
                  Performance Overview
                </button>
                <button
                  onClick={() => setActiveTab('agents')}
                  className={`px-8 py-4 font-bold transition-all duration-300 ${
                    activeTab === 'agents' 
                      ? 'text-cyan-400 border-b-2 border-cyan-400 bg-cyan-400/5' 
                      : 'text-gray-400 hover:text-cyan-300'
                  }`}
                >
                  Agent Analytics
                </button>
              </div>
            </div>

            <div className="p-8">
              {activeTab === 'overview' && (
                <div className="space-y-8">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="bg-gray-700/30 rounded-xl p-6">
                      <h4 className="text-cyan-100 font-bold text-lg mb-4 flex items-center gap-2">
                        <FiTrendingUp className="text-cyan-400" />
                        Performance Metrics
                      </h4>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-300">Efficiency Rating</span>
                          <div className="flex items-center gap-3">
                            <div className="w-32 bg-gray-600 rounded-full h-2">
                              <div 
                                className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${analytics.efficiency}%` }}
                              ></div>
                            </div>
                            <span className="text-cyan-400 font-semibold">{analytics.efficiency}%</span>
                          </div>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-300">Reliability Score</span>
                          <div className="flex items-center gap-3">
                            <div className="w-32 bg-gray-600 rounded-full h-2">
                              <div 
                                className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all duration-500"
                                style={{ width: `${analytics.reliability}%` }}
                              ></div>
                            </div>
                            <span className="text-green-400 font-semibold">{analytics.reliability}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-gray-700/30 rounded-xl p-6">
                      <h4 className="text-cyan-100 font-bold text-lg mb-4 flex items-center gap-2">
                        <FiBarChart className="text-cyan-400" />
                        Weekly Performance Trend
                      </h4>
                      <div className="grid grid-cols-7 gap-2">
                        {[78, 82, 85, 79, 88, 86, 92].map((score, index) => (
                          <div key={index} className="text-center">
                            <div className="bg-gray-600 rounded h-24 mb-2 flex items-end p-1">
                              <div 
                                className="w-full bg-gradient-to-t from-cyan-500 to-blue-600 rounded transition-all duration-500"
                                style={{ height: `${score}%` }}
                              ></div>
                            </div>
                            <div className="text-xs text-gray-400">
                              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-700/30 rounded-xl p-6">
                    <h4 className="text-cyan-100 font-bold text-lg mb-4">Recent Achievements</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-lg p-4 border border-yellow-500/30">
                        <div className="text-2xl mb-2">🏆</div>
                        <div className="font-semibold text-yellow-400">High Performer</div>
                        <div className="text-sm text-gray-300">Achieved 90%+ score</div>
                      </div>
                      <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-lg p-4 border border-green-500/30">
                        <div className="text-2xl mb-2">⚡</div>
                        <div className="font-semibold text-green-400">Speed Demon</div>
                        <div className="text-sm text-gray-300">Sub-second response</div>
                      </div>
                      <div className="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-lg p-4 border border-blue-500/30">
                        <div className="text-2xl mb-2">🎯</div>
                        <div className="font-semibold text-blue-400">Consistent</div>
                        <div className="text-sm text-gray-300">7-day streak</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'agents' && (
                <div>
                  {agents.length === 0 ? (
                    <div className="text-center py-12">
                      <FiCpu className="text-6xl text-cyan-400 mx-auto mb-4" />
                      <h3 className="text-xl font-bold text-cyan-100 mb-3">No Agents Created</h3>
                      <p className="text-cyan-300 mb-6">Create your first AI agent to start benchmarking and analytics!</p>
                      <Link 
                        to="/agents/create"
                        className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white px-6 py-3 rounded-xl font-bold inline-flex items-center gap-2 transition-all duration-300"
                      >
                        Create Agent
                      </Link>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {agents.map((agent) => {
                        const metrics = getAgentMetrics(agent);
                        return (
                          <div
                            key={agent.id}
                            className="bg-gray-700/30 rounded-xl p-6 hover:bg-gray-700/40 transition-all duration-300"
                          >
                            <div className="flex items-center justify-between mb-4">
                              <div className="flex items-center gap-4">
                                <div className="text-2xl">
                                  {agent.agentType === 'gpt-4' ? '🧠' : 
                                   agent.agentType === 'gpt-3.5-turbo' ? '⚡' : 
                                   agent.agentType === 'claude-3' ? '🤖' : '🔧'}
                                </div>
                                <div>
                                  <h4 className="font-bold text-cyan-100 text-lg">{agent.name}</h4>
                                  <div className="text-sm text-gray-400">{agent.agentType}</div>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="flex items-center gap-2 mb-1">
                                  <FiTrendingUp className={`text-sm ${metrics.trend === 'up' ? 'text-green-400' : 'text-red-400'}`} />
                                  <span className={`font-bold ${metrics.trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                                    {metrics.avgScore}%
                                  </span>
                                </div>
                                <div className="text-xs text-gray-400">Average Score</div>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-3 gap-6 text-sm">
                              <div className="text-center">
                                <div className="text-cyan-400 font-bold text-lg">{metrics.testsRun}</div>
                                <div className="text-gray-400">Tests Run</div>
                              </div>
                              <div className="text-center">
                                <div className="text-blue-400 font-bold text-lg">{metrics.lastRun}</div>
                                <div className="text-gray-400">Last Test</div>
                              </div>
                              <div className="text-center">
                                <div className={`font-bold text-lg ${agent.isActive ? 'text-green-400' : 'text-red-400'}`}>
                                  {agent.isActive ? 'Active' : 'Inactive'}
                                </div>
                                <div className="text-gray-400">Status</div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </HomeLayout>
  );
}

export default UserProfile;