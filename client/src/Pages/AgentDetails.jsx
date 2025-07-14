import { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiCpu, FiKey, FiEdit, FiTrash2, FiZap, FiTarget, FiTrendingUp, FiSettings } from 'react-icons/fi';
import HomeLayout from '../Layouts/HomeLayout';
import axiosInstance from '../Helper/axiosInstance';
import toast from 'react-hot-toast';

function AgentDetails() {
  const { agentId } = useParams();
  const navigate = useNavigate();
  const [agent, setAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState({
    overallScore: 0,
    efficiency: 0,
    reliability: 0,
    accuracy: 0,
    testsRun: 0,
    avgResponseTime: 0
  });

  useEffect(() => {
    const fetchAgentDetails = async () => {
      try {
        const response = await axiosInstance.get(`/agents/${agentId}`);
        setAgent(response.data);

        // In a real app, we'd fetch actual performance data
        // Here we're creating mock data
        setTimeout(() => {
          setPerformanceData({
            overallScore: Math.round(70 + Math.random() * 20),
            efficiency: Math.round(65 + Math.random() * 30),
            reliability: Math.round(75 + Math.random() * 20),
            accuracy: Math.round(70 + Math.random() * 25),
            testsRun: Math.floor(10 + Math.random() * 40),
            avgResponseTime: Math.round((0.5 + Math.random() * 2) * 100) / 100
          });
          setLoading(false);
        }, 800);
      } catch (error) {
        console.error('Error fetching agent details:', error);
        toast.error('Failed to load agent details');
        setLoading(false);
      }
    };

    fetchAgentDetails();
  }, [agentId]);

  const handleDeleteAgent = async () => {
    if (!window.confirm('Are you sure you want to delete this agent?')) return;
    
    try {
      await axiosInstance.delete(`/agents/${agentId}`);
      toast.success('Agent deleted successfully');
      navigate('/agents');
    } catch (error) {
      console.error('Error deleting agent:', error);
      toast.error('Failed to delete agent');
    }
  };

  const getAgentTypeIcon = (type) => {
    switch (type) {
      case 'gpt-4': return '🤖';
      case 'gpt-3.5-turbo': return '⚡';
      case 'claude-3': return '🧠';
      case 'custom': return '🔧';
      default: return '🤖';
    }
  };

  const getAgentTypeColor = (type) => {
    switch (type) {
      case 'gpt-4': return 'from-emerald-500 to-green-600';
      case 'gpt-3.5-turbo': return 'from-yellow-500 to-orange-600';
      case 'claude-3': return 'from-purple-500 to-violet-600';
      case 'custom': return 'from-blue-500 to-indigo-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 75) return 'text-yellow-400';
    if (score >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

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
      <div className="min-h-[90vh] py-12 px-8 text-white bg-gradient-to-br from-gray-900 via-blue-900/20 to-cyan-900/20">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Link 
              to="/agents"
              className="text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              <FiArrowLeft className="text-2xl" />
            </Link>
            <h1 className="text-4xl font-bold text-cyan-100">Agent Details</h1>
          </div>

          {agent && (
            <div className="space-y-8">
              <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-6">
                    <div className={`w-20 h-20 bg-gradient-to-br ${getAgentTypeColor(agent.agentType || 'gpt-4')} rounded-xl flex items-center justify-center text-4xl`}>
                      {getAgentTypeIcon(agent.agentType || 'gpt-4')}
                    </div>
                    <div>
                      <h2 className="text-3xl font-bold text-cyan-100">{agent.name}</h2>
                      <div className={`bg-gradient-to-r ${getAgentTypeColor(agent.agentType || 'gpt-4')} text-white px-3 py-1 rounded-full font-bold text-sm inline-block mt-2`}>
                        {agent.agentType || 'gpt-4'}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => navigate(`/agents/${agentId}/edit`)}
                      className="bg-gradient-to-r from-yellow-500/20 to-amber-600/20 hover:from-yellow-500/30 hover:to-amber-600/30 text-yellow-400 py-2 px-4 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2"
                    >
                      <FiEdit /> Edit
                    </button>
                    <button
                      onClick={handleDeleteAgent}
                      className="bg-gradient-to-r from-red-500/20 to-rose-600/20 hover:from-red-500/30 hover:to-rose-600/30 text-red-400 py-2 px-4 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2"
                    >
                      <FiTrash2 /> Delete
                    </button>
                  </div>
                </div>

                {agent.description && (
                  <div className="mt-6">
                    <h3 className="text-xl font-semibold text-cyan-200 mb-2">Description</h3>
                    <p className="text-gray-300 leading-relaxed">{agent.description}</p>
                  </div>
                )}

                <div className="mt-6">
                  <h3 className="text-xl font-semibold text-cyan-200 mb-3">Agent Configuration</h3>
                  <div className="bg-gray-800/50 rounded-xl p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Type</span>
                        <span className="text-cyan-400 font-semibold">{agent.agentType || 'gpt-4'}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">API Key</span>
                        <span className="text-cyan-400 font-semibold">{agent.hasApiKey ? 'Configured' : 'Not Configured'}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Created</span>
                        <span className="text-cyan-400 font-semibold">{new Date(agent.created_at || Date.now()).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Status</span>
                        <span className="text-green-400 font-semibold flex items-center gap-1">
                          <span className="w-2 h-2 bg-green-400 rounded-full inline-block"></span> Active
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20">
                <h3 className="text-2xl font-bold text-cyan-100 mb-6">Performance Metrics</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <div className="bg-gray-800/50 p-4 rounded-xl text-center">
                    <div className={`text-3xl font-bold ${getPerformanceColor(performanceData.overallScore)}`}>
                      {performanceData.overallScore}%
                    </div>
                    <div className="text-gray-400 mt-1">Overall Score</div>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-xl text-center">
                    <div className="text-3xl font-bold text-cyan-400">
                      {performanceData.testsRun}
                    </div>
                    <div className="text-gray-400 mt-1">Tests Run</div>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-xl text-center">
                    <div className="text-3xl font-bold text-yellow-400">
                      {performanceData.avgResponseTime}s
                    </div>
                    <div className="text-gray-400 mt-1">Avg Response Time</div>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-xl text-center">
                    <div className={`text-3xl font-bold ${getPerformanceColor(performanceData.accuracy)}`}>
                      {performanceData.accuracy}%
                    </div>
                    <div className="text-gray-400 mt-1">Accuracy</div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Efficiency</span>
                      <span className="text-cyan-400">{performanceData.efficiency}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${performanceData.efficiency}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Reliability</span>
                      <span className="text-green-400">{performanceData.reliability}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${performanceData.reliability}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Accuracy</span>
                      <span className="text-yellow-400">{performanceData.accuracy}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-yellow-500 to-orange-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${performanceData.accuracy}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Link 
                  to="/tasks" 
                  state={{ preselectedAgent: agent }}
                  className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 flex items-center justify-between group hover:border-cyan-400/40 transition-all duration-300"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center">
                      <FiZap className="text-xl text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-cyan-100">Benchmark Agent</h3>
                      <p className="text-gray-400">Run agent against available tasks</p>
                    </div>
                  </div>
                  <div className="group-hover:translate-x-2 transition-transform">→</div>
                </Link>

                <Link 
                  to="/agents"
                  className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 flex items-center justify-between group hover:border-cyan-400/40 transition-all duration-300"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl flex items-center justify-center">
                      <FiTrendingUp className="text-xl text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-cyan-100">Compare with Others</h3>
                      <p className="text-gray-400">View performance against other agents</p>
                    </div>
                  </div>
                  <div className="group-hover:translate-x-2 transition-transform">→</div>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </HomeLayout>
  );
}

export default AgentDetails; 