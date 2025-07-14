import { useEffect, useState } from 'react';
import { FiStar, FiUsers, FiTarget, FiClock, FiFilter, FiZap, FiCpu, FiAward, FiChevronRight } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import axiosInstance from '../Helper/axiosInstance';
import HomeLayout from '../Layouts/HomeLayout';
import toast from 'react-hot-toast';

function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [agents, setAgents] = useState([]);
  const [selectedTask, setSelectedTask] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('');
  const [sortBy, setSortBy] = useState('score');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedTask) {
      fetchLeaderboard(selectedTask);
    }
  }, [selectedTask, sortBy]);

  const fetchData = async () => {
    try {
      const [tasksResponse, agentsResponse] = await Promise.all([
        axiosInstance.get('/tasks'),
        axiosInstance.get('/agents')
      ]);
      
      const tasksData = tasksResponse.data?.items || tasksResponse.data || [];
      setTasks(tasksData);
      setAgents(agentsResponse.data?.agents || []);

      if (tasksData.length > 0) {
        setSelectedTask(tasksData[0].id);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load tasks or agents');
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaderboard = async (taskId) => {
    try {
      const response = await axiosInstance.get(`/tasks/${taskId}/leaderboard?sort_by=${sortBy}`);
      let leaderboardData = response.data || [];
      
      if (selectedAgent) {
        leaderboardData = leaderboardData.filter(entry => entry.agentId === selectedAgent);
      }
      
      setLeaderboard(leaderboardData);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      setLeaderboard([]);
    }
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return '🏅';
    }
  };

  const getRankColor = (rank) => {
    switch (rank) {
      case 1:
        return 'from-yellow-400 to-yellow-600';
      case 2:
        return 'from-gray-300 to-gray-500';
      case 3:
        return 'from-amber-600 to-amber-800';
      default:
        return 'from-cyan-500 to-blue-600';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-cyan-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

  const getModelBadge = (modelId) => {
    if (!modelId) return null;
    
    const modelLower = modelId.toLowerCase();
    let bgColor = 'bg-gray-700';
    let textColor = 'text-gray-200';
    let icon = null;
    
    if (modelLower.includes('gpt-4')) {
      bgColor = 'bg-green-900';
      textColor = 'text-green-200';
      icon = '🧠';
    } else if (modelLower.includes('gpt-3.5')) {
      bgColor = 'bg-green-800';
      textColor = 'text-green-200';
      icon = '⚡';
    } else if (modelLower.includes('claude')) {
      bgColor = 'bg-purple-900';
      textColor = 'text-purple-200';
      icon = '🔮';
    } else if (modelLower.includes('gemini')) {
      bgColor = 'bg-blue-900';
      textColor = 'text-blue-200';
      icon = '🌌';
    }
    
    return (
      <span className={`${bgColor} ${textColor} text-xs px-2 py-1 rounded-full flex items-center gap-1`}>
        {icon && <span>{icon}</span>}
        {modelId}
      </span>
    );
  };

  const getAccuracyBar = (accuracy) => {
    const percentage = accuracy * 100;
    let barColor = 'bg-red-500';
    
    if (percentage >= 90) barColor = 'bg-green-500';
    else if (percentage >= 80) barColor = 'bg-cyan-500';
    else if (percentage >= 70) barColor = 'bg-yellow-500';
    else if (percentage >= 60) barColor = 'bg-orange-500';
    
    return (
      <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
        <div 
          className={`${barColor} h-2 rounded-full`} 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    );
  };

  if (loading) {
    return (
      <HomeLayout>
        <div className="min-h-[90vh] pt-12 px-8 flex flex-col items-center justify-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400 mb-4"></div>
          <p className="text-cyan-200">Loading leaderboard...</p>
        </div>
      </HomeLayout>
    );
  }

  // Find the selected task object
  const selectedTaskObj = tasks.find(task => task.id === selectedTask);

  return (
    <HomeLayout>
      <div className="min-h-[90vh] pt-12 px-8 text-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent flex items-center justify-center gap-3">
              <FiAward className="text-cyan-400" />
              Agent Leaderboard
            </h1>
            <p className="text-cyan-200 mt-2">Performance rankings across benchmark tasks</p>
          </div>

          {/* Task information card */}
          {selectedTaskObj && (
            <div className="mb-8 bg-gray-800/50 border border-cyan-500/20 rounded-xl p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-white">{selectedTaskObj.title}</h2>
                  <p className="text-cyan-300 mt-1">{selectedTaskObj.description?.substring(0, 120)}...</p>
                  <div className="flex items-center gap-3 mt-3">
                    <span className="bg-gray-700 text-cyan-300 text-xs px-3 py-1 rounded-full">
                      {selectedTaskObj.difficulty || 'MEDIUM'}
                    </span>
                    <span className="bg-gray-700 text-cyan-300 text-xs px-3 py-1 rounded-full">
                      {selectedTaskObj.webArenaEnvironment || 'Generic'} Environment
                    </span>
                    <span className="bg-gray-700 text-cyan-300 text-xs px-3 py-1 rounded-full flex items-center gap-1">
                      <FiUsers className="text-cyan-400" />
                      {leaderboard.length} Submissions
                    </span>
                  </div>
                </div>
                <Link
                  to="/playground"
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white py-2 px-6 rounded-lg flex items-center gap-2 transition-all"
                >
                  Try This Task <FiChevronRight />
                </Link>
              </div>
            </div>
          )}

          <div className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <FiTarget className="text-cyan-400" />
                <label className="text-cyan-200 font-medium">Task:</label>
                <select
                  value={selectedTask}
                  onChange={(e) => setSelectedTask(e.target.value)}
                  className="bg-gray-700 border border-gray-600 px-4 py-2 rounded-lg text-white focus:border-cyan-500 focus:outline-none flex-1"
                >
                  {tasks.map((task) => (
                    <option key={task.id} value={task.id}>
                      {task.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <FiCpu className="text-cyan-400" />
                <label className="text-cyan-200 font-medium">Agent:</label>
                <select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  className="bg-gray-700 border border-gray-600 px-4 py-2 rounded-lg text-white focus:border-cyan-500 focus:outline-none flex-1"
                >
                  <option value="">All Agents</option>
                  {agents.map((agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <FiFilter className="text-cyan-400" />
                <label className="text-cyan-200 font-medium">Sort By:</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-gray-700 border border-gray-600 px-4 py-2 rounded-lg text-white focus:border-cyan-500 focus:outline-none flex-1"
                >
                  <option value="score">Overall Score</option>
                  <option value="accuracy">Accuracy</option>
                  <option value="time">Time Taken</option>
                </select>
              </div>
            </div>
          </div>

          {leaderboard.length === 0 ? (
            <div className="text-center py-16">
              <div className="bg-gray-800 rounded-lg p-8 border border-cyan-500/20 max-w-md mx-auto">
                <FiStar className="text-6xl text-cyan-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-cyan-100 mb-2">No Results Yet</h3>
                <p className="text-cyan-300 mb-4">Be the first to submit an agent to this task!</p>
                <Link
                  to="/playground"
                  className="inline-block bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white py-2 px-6 rounded-lg transition-all"
                >
                  Go to Playground
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {leaderboard.slice(0, 3).map((entry) => (
                <div
                  key={entry.submissionId}
                  className={`bg-gradient-to-r ${getRankColor(entry.rank)} p-6 rounded-lg shadow-lg border-2 border-opacity-50`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="text-4xl">{getRankIcon(entry.rank)}</div>
                      <div>
                        <h3 className="text-xl font-bold text-white">{entry.agentName}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          {getModelBadge(entry.modelId)}
                          <span className="text-white/80 text-sm">Rank #{entry.rank}</span>
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-4xl font-bold text-white mb-1">{entry.score.toFixed(1)}</div>
                      <div className="text-white/80 text-sm">Score</div>
                    </div>
                  </div>

                  <div className="mt-4 grid grid-cols-3 gap-6">
                    <div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-white/90">
                          <FiClock className="text-cyan-400" />
                          <span className="font-medium">Time</span>
                        </div>
                        <span className="text-white font-bold">{entry.timeTaken?.toFixed(1)}s</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `${Math.min(100, (entry.timeTaken / 120) * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-white/90">
                          <FiTarget className="text-cyan-400" />
                          <span className="font-medium">Accuracy</span>
                        </div>
                        <span className="text-white font-bold">{(entry.accuracy * 100).toFixed(1)}%</span>
                      </div>
                      {getAccuracyBar(entry.accuracy)}
                    </div>
                    
                    <div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-white/90">
                          <FiZap className="text-cyan-400" />
                          <span className="font-medium">Efficiency</span>
                        </div>
                        <span className="text-white font-bold">{(entry.metrics?.efficiency || 0).toFixed(2)}</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
                        <div 
                          className="bg-yellow-500 h-2 rounded-full" 
                          style={{ width: `${(entry.metrics?.efficiency || 0) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex justify-end">
                    <Link 
                      to={`/submissions/${entry.submissionId}`} 
                      className="text-sm text-cyan-300 hover:text-cyan-100 flex items-center gap-1"
                    >
                      View Details <FiChevronRight />
                    </Link>
                  </div>
                </div>
              ))}

              {leaderboard.length > 3 && (
                <div className="bg-gray-800 rounded-lg border border-cyan-500/20 overflow-hidden">
                  <div className="bg-gray-700 px-6 py-3 border-b border-gray-600 flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-cyan-100">Other Rankings</h3>
                    <div className="flex gap-4 text-xs text-gray-300">
                      <div className="w-24 text-right">Accuracy</div>
                      <div className="w-24 text-right">Time</div>
                      <div className="w-24 text-right">Score</div>
                    </div>
                  </div>

                  <div className="divide-y divide-gray-700">
                    {leaderboard.slice(3).map((entry) => (
                      <div key={entry.submissionId} className="px-6 py-4 hover:bg-gray-750 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                              {entry.rank}
                            </div>
                            <div>
                              <h4 className="font-semibold text-cyan-100">{entry.agentName}</h4>
                              <div className="flex gap-2 text-xs text-gray-400 mt-1">
                                {getModelBadge(entry.modelId)}
                                <Link 
                                  to={`/submissions/${entry.submissionId}`} 
                                  className="text-cyan-300 hover:text-cyan-100 flex items-center gap-1"
                                >
                                  View Details <FiChevronRight className="text-xs" />
                                </Link>
                              </div>
                            </div>
                          </div>

                          <div className="flex gap-4 text-sm">
                            <div className="w-24 text-right">{(entry.accuracy * 100).toFixed(1)}%</div>
                            <div className="w-24 text-right">{entry.timeTaken?.toFixed(1)}s</div>
                            <div className={`w-24 text-right font-bold ${getScoreColor(entry.score)}`}>
                              {entry.score.toFixed(1)}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </HomeLayout>
  );
}

export default Leaderboard;
