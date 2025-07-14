import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiPlus, FiCpu, FiKey, FiZap, FiTarget, FiTrendingUp, FiActivity, FiEdit, FiTrash2 } from 'react-icons/fi';
import axiosInstance from '../Helper/axiosInstance';
import HomeLayout from '../Layouts/HomeLayout';
import toast from 'react-hot-toast';

function DisplayAgents() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await axiosInstance.get('/agents');
      const data = response.data;
      if (Array.isArray(data)) setAgents(data);
      else if (data?.items && Array.isArray(data.items)) setAgents(data.items);
      else setAgents([]);
    } catch {
      toast.error('Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleBenchmarkAgent = (agent) => {
    setSelectedAgent(agent);
    navigate('/playground', { state: { preselectedAgent: agent } });
  };

  const handleDeleteAgent = async (agentId) => {
    if (!window.confirm('Are you sure you want to delete this agent?')) return;
    try {
      await axiosInstance.delete(`/agents/${agentId}`);
      toast.success('Agent deleted successfully');
      fetchAgents();
    } catch {
      toast.error('Failed to delete agent');
    }
  };

  const getAgentTypeIcon = (type = '') => {
    switch (type) {
      case 'gpt-4':
        return '🤖';
      case 'gpt-3.5-turbo':
        return '⚡';
      case 'claude-3':
        return '🧠';
      case 'custom':
        return '🔧';
      default:
        return '🤖';
    }
  };

  const getAgentTypeColor = (type = '') => {
    switch (type) {
      case 'gpt-4':
        return 'from-emerald-500 to-green-600';
      case 'gpt-3.5-turbo':
        return 'from-yellow-500 to-orange-600';
      case 'claude-3':
        return 'from-purple-500 to-violet-600';
      case 'custom':
        return 'from-blue-500 to-indigo-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 75) return 'text-yellow-400';
    if (score >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

  const generateMockMetrics = () => {
    return {
      overallScore: Math.round(65 + Math.random() * 30),
      efficiency: Math.round(70 + Math.random() * 25),
      reliability: Math.round(80 + Math.random() * 20),
      testsRun: Math.floor(Math.random() * 50) + 10,
      avgResponseTime: (0.5 + Math.random() * 2).toFixed(2),
    };
  };

  if (loading) {
    return (
      <HomeLayout>
        <div className="min-h-[90vh] pt-12 px-8 flex flex-col items-center justify-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mb-4"></div>
          <p className="text-cyan-200">Loading agents...</p>
        </div>
      </HomeLayout>
    );
  }

  return (
    <HomeLayout>
      <div className="min-h-[90vh] pt-12 px-8 text-white bg-gradient-to-br from-gray-900 via-blue-900/20 to-cyan-900/20">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-12">
            <div className="space-y-4">
              <h1 className="text-5xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                Agent Benchmark Hub
              </h1>
              <p className="text-xl text-cyan-200">Manage, analyze, and optimize your AI agents</p>
              <div className="flex items-center gap-6 text-sm text-cyan-300">
                <div className="flex items-center gap-2">
                  <FiActivity className="text-cyan-400" />
                  <span>{agents.length} Active Agents</span>
                </div>
                <div className="flex items-center gap-2">
                  <FiTarget className="text-green-400" />
                  <span>Real-time Monitoring</span>
                </div>
              </div>
            </div>
            <Link
              to="/agents/create"
              className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white px-8 py-4 rounded-xl font-bold flex items-center gap-3 transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/25"
            >
              <FiPlus className="text-xl" /> Create New Agent
            </Link>
          </div>

          {agents.length === 0 ? (
            <div className="text-center py-20">
              <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg rounded-2xl p-12 border border-cyan-500/20 max-w-2xl mx-auto">
                <div className="w-24 h-24 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
                  <FiCpu className="text-4xl text-white" />
                </div>
                <h3 className="text-2xl font-bold text-cyan-100 mb-4">No Agents Found</h3>
                <p className="text-cyan-300 mb-8 text-lg">
                  Create your first AI agent to start benchmarking and performance analysis!
                </p>
                <Link
                  to="/agents/create"
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white px-8 py-4 rounded-xl font-bold inline-flex items-center gap-3 transition-all duration-300 transform hover:scale-105"
                >
                  <FiPlus /> Create First Agent
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
              {agents.map((agent) => {
                const metrics = generateMockMetrics();
                return (
                  <div
                    key={agent?.id || Math.random()}
                    className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl shadow-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300 hover:scale-105 group"
                  >
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex items-center gap-4">
                        <div className="text-4xl">{getAgentTypeIcon(agent?.agentType)}</div>
                        <div>
                          <h2 className="text-xl font-bold text-cyan-100">{agent?.name}</h2>
                          <div
                            className={`bg-gradient-to-r ${getAgentTypeColor(agent?.agentType)} text-white text-xs px-3 py-1 rounded-full font-bold inline-block mt-1`}
                          >
                            {agent?.agentType}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {agent?.hasApiKey && <FiKey className="text-green-400 text-lg" />}
                        <div
                          className={`w-4 h-4 rounded-full ${agent?.isActive ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}
                        ></div>
                      </div>
                    </div>

                    <div className="bg-gray-700/30 rounded-xl p-4 mb-6">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="text-center">
                          <div className={`text-2xl font-bold ${getPerformanceColor(metrics.overallScore)}`}>
                            {metrics.overallScore}%
                          </div>
                          <div className="text-gray-400">Overall Score</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-cyan-400">{metrics.testsRun}</div>
                          <div className="text-gray-400">Tests Run</div>
                        </div>
                      </div>
                      <div className="mt-4 space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Efficiency</span>
                          <span className="text-cyan-400">{metrics.efficiency}%</span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full"
                            style={{ width: `${metrics.efficiency}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="mt-3 space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Reliability</span>
                          <span className="text-green-400">{metrics.reliability}%</span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full"
                            style={{ width: `${metrics.reliability}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    {agent?.description && (
                      <p className="text-gray-300 mb-6 text-sm leading-relaxed">{agent.description}</p>
                    )}

                    <div className="flex items-center justify-between text-xs text-gray-400 mb-6">
                      <span>Created: {agent?.createdAt ? new Date(agent.createdAt).toLocaleDateString() : 'N/A'}</span>
                      <span>Avg Response: {metrics.avgResponseTime}s</span>
                    </div>

                    <div className="flex gap-3">
                      <button
                        onClick={() => handleBenchmarkAgent(agent)}
                        className="flex-1 bg-gradient-to-r from-cyan-500/20 to-blue-600/20 hover:from-cyan-500/30 hover:to-blue-600/30 text-cyan-400 py-3 rounded-xl font-bold transition-all duration-300 flex items-center justify-center gap-2"
                      >
                        <FiZap className="text-lg" /> Benchmark
                      </button>
                      <button
                        onClick={() => {
                          setSelectedAgent({ ...agent, metrics });
                          setShowDetailsModal(true);
                        }}
                        className="px-4 py-3 bg-gray-700/50 hover:bg-gray-600/50 text-gray-300 hover:text-cyan-400 rounded-xl transition-all duration-300"
                      >
                        <FiTrendingUp className="text-lg" />
                      </button>
                      <button
                        onClick={() => navigate(`/agents/edit/${agent?.id}`)}
                        className="px-4 py-3 bg-gray-700/50 hover:bg-gray-600/50 text-gray-300 hover:text-yellow-400 rounded-xl transition-all duration-300"
                      >
                        <FiEdit className="text-lg" />
                      </button>
                      <button
                        onClick={() => handleDeleteAgent(agent?.id)}
                        className="px-4 py-3 bg-gray-700/50 hover:bg-red-600/50 text-gray-300 hover:text-red-400 rounded-xl transition-all duration-300"
                      >
                        <FiTrash2 className="text-lg" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </HomeLayout>
  );
}

export default DisplayAgents;
