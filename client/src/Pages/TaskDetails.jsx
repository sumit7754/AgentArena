import { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiUsers, FiAward, FiCpu, FiTarget, FiCheck } from 'react-icons/fi';
import axiosInstance from '../Helper/axiosInstance';
import HomeLayout from '../Layouts/HomeLayout';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

function TaskDetails() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);

  useEffect(() => {
    if (taskId) {
      fetchTaskDetails();
      fetchUserAgents();
    }
  }, [taskId]);

  const fetchTaskDetails = async () => {
    try {
      const response = await axiosInstance.get(`/tasks/${taskId}`);
      setTask(response.data);
    } catch (error) {
      console.error('Error fetching task details:', error);
      toast.error('Failed to load task details');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserAgents = async () => {
    if (!isAuthenticated) return;
    
    try {
      const response = await axiosInstance.get('/agents');
      setAgents(response.data.agents || response.data.items || []);
    } catch (error) {
      console.error('Error fetching agents:', error);
      toast.error('Failed to load your agents');
    }
  };

  const handleRunWithAgent = (agent) => {
    setSelectedAgent(agent);
    navigate('/playground', { state: { preselectedAgent: agent, preselectedTask: task } });
  };

  const getDifficultyColor = (difficulty) => {
    if (!difficulty) return 'from-blue-500 to-indigo-600';
    
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'from-green-500 to-emerald-600';
      case 'medium': return 'from-yellow-500 to-orange-600';
      case 'hard': return 'from-red-500 to-rose-600';
      default: return 'from-blue-500 to-indigo-600';
    }
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
  
  if (!task) {
    return (
      <HomeLayout>
        <div className="min-h-[90vh] flex flex-col items-center justify-center">
          <h2 className="text-2xl text-cyan-400 mb-4">Task Not Found</h2>
          <p className="text-gray-300 mb-6">The task you're looking for doesn't exist or has been removed.</p>
          <Link to="/tasks" className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-6 py-3 rounded-xl">
            Return to Tasks
          </Link>
        </div>
      </HomeLayout>
    );
  }

  return (
    <HomeLayout>
      <div className="min-h-[90vh] py-12 px-8 text-white bg-gradient-to-br from-gray-900 via-blue-900/20 to-cyan-900/20">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <Link to="/tasks" className="text-cyan-400 hover:text-cyan-300 transition-colors inline-flex items-center gap-2">
              <FiArrowLeft /> Back to Tasks
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Task Details */}
            <div className="lg:col-span-2 bg-gray-800/50 backdrop-blur-lg rounded-2xl p-8 border border-cyan-500/20">
              <div className="flex items-center gap-4 mb-6">
                <div className={`w-16 h-16 bg-gradient-to-br ${getDifficultyColor(task.difficulty)} rounded-xl flex items-center justify-center text-3xl`}>
                  {task.webArenaEnvironment?.charAt(0) || '🎯'}
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                    {task.title}
                  </h1>
                  <div className="flex items-center gap-4 mt-2">
                    <div className={`px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${getDifficultyColor(task.difficulty)}`}>
                      {task.difficulty || 'Standard'} Difficulty
                    </div>
                    <div className="flex items-center gap-1 text-cyan-200">
                      <FiTarget className="text-cyan-400" />
                      <span>{task.webArenaEnvironment || 'Standard'} Environment</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="prose prose-invert max-w-none mb-8">
                <h2 className="text-xl font-semibold text-cyan-100 mb-3">Task Description</h2>
                <p className="text-gray-300">{task.description}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-gray-700/50 rounded-xl p-5 border border-cyan-500/10">
                  <h3 className="text-lg font-semibold text-cyan-100 mb-3">Time Expectations</h3>
                  <div className="flex items-center gap-3 text-gray-300">
                    <FiClock className="text-yellow-400 text-xl" />
                    <div>
                      <p>Expected Completion: <span className="text-white font-medium">{task.expectedCompletionTime || 300}s</span></p>
                      <p>Maximum Time Allowed: <span className="text-white font-medium">{task.maxAllowedTime || 600}s</span></p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-700/50 rounded-xl p-5 border border-cyan-500/10">
                  <h3 className="text-lg font-semibold text-cyan-100 mb-3">Performance Metrics</h3>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <FiCheck className="text-green-400" />
                      <span className="text-gray-300">Task completion accuracy</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FiCheck className="text-green-400" />
                      <span className="text-gray-300">Time taken to complete</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FiCheck className="text-green-400" />
                      <span className="text-gray-300">Resource efficiency</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 mb-8">
                <Link 
                  to={`/tasks/${task.id}/leaderboard`}
                  className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2"
                >
                  <FiAward /> View Leaderboard
                </Link>
                <button 
                  onClick={() => navigate('/playground', { state: { preselectedTask: task } })}
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300"
                >
                  Try in Playground
                </button>
              </div>
            </div>

            {/* Agent Selection Panel */}
            <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-cyan-500/20 h-fit">
              <h2 className="text-xl font-bold text-cyan-100 mb-4 flex items-center gap-2">
                <FiCpu className="text-cyan-400" />
                Run with Your Agent
              </h2>

              {!isAuthenticated ? (
                <div className="text-center py-8">
                  <p className="text-cyan-200 mb-4">Please login to test this task with your agent</p>
                  <Link
                    to="/login"
                    className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 px-6 py-3 rounded-xl font-semibold transition-all duration-300 inline-block"
                  >
                    Login Now
                  </Link>
                </div>
              ) : agents.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-cyan-200 mb-4">You haven't created any agents yet</p>
                  <Link
                    to="/agents/create"
                    className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 px-6 py-3 rounded-xl font-semibold transition-all duration-300 inline-block"
                  >
                    Create an Agent
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {agents.map((agent) => (
                    <div
                      key={agent.id}
                      className="p-4 rounded-xl border border-gray-600 hover:border-cyan-500/50 hover:bg-gray-700/50 cursor-pointer transition-all duration-300"
                      onClick={() => handleRunWithAgent(agent)}
                    >
                      <h4 className="font-semibold text-white">{agent.name}</h4>
                      <p className="text-cyan-200 text-sm my-2">
                        {agent.description || 'No description available'}
                      </p>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                          {agent.configurationJson?.llm_model || agent.agentType || 'Unknown'}
                        </span>
                        <span className={`px-2 py-1 ${agent.configType === 'mock' ? 'bg-purple-500/20 text-purple-400' : 'bg-green-500/20 text-green-400'} rounded`}>
                          {agent.configType === 'mock' ? 'Mock' : 'Real'} Config
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </HomeLayout>
  );
}

export default TaskDetails; 