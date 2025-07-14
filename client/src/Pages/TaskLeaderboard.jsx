import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { FiArrowLeft, FiAward, FiTrendingUp, FiTarget, FiCpu } from 'react-icons/fi';
import HomeLayout from '../Layouts/HomeLayout';
import axiosInstance from '../Helper/axiosInstance';
import toast from 'react-hot-toast';

function TaskLeaderboard() {
  const { taskId } = useParams();
  const [task, setTask] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (taskId) {
      fetchTaskData();
    }
  }, [taskId]);
  
  const fetchTaskData = async () => {
    try {
      const [taskResponse, leaderboardResponse] = await Promise.all([
        axiosInstance.get(`/tasks/${taskId}`),
        axiosInstance.get(`/tasks/${taskId}/leaderboard`)
      ]);
      
      setTask(taskResponse.data);
      setLeaderboard(leaderboardResponse.data || []);
    } catch (error) {
      console.error('Error fetching task data:', error);
      toast.error('Failed to load task data');
    } finally {
      setLoading(false);
    }
  };

  const getAgentTypeIcon = (type) => {
    if (!type) return '🤖';
    
    switch (type.toLowerCase()) {
      case 'gpt-4': return '🤖';
      case 'gpt-3.5-turbo': return '⚡';
      case 'claude-3': return '🧠';
      case 'custom': return '🔧';
      case 'real': return '🔌';
      case 'mock': return '🧪';
      default: return '🤖';
    }
  };

  const getRankColor = (rank) => {
    switch (rank) {
      case 1: return 'from-yellow-400 to-amber-600';
      case 2: return 'from-gray-300 to-gray-500';
      case 3: return 'from-amber-700 to-yellow-800';
      default: return 'from-gray-600 to-gray-800';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-cyan-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
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
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Link 
              to="/leaderboard"
              className="text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              <FiArrowLeft className="text-2xl" />
            </Link>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                Task Leaderboard
              </h1>
              <div className="flex items-center gap-2 mt-2">
                <FiTarget className="text-cyan-400" />
                <span className="text-lg text-cyan-200">{task.title}</span>
                <span className="bg-gray-700/50 text-gray-300 text-xs px-2 py-1 rounded-md ml-2">
                  {task.difficulty}
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-8">
            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <FiAward className="text-3xl text-yellow-400" />
                  <h2 className="text-2xl font-bold text-cyan-100">Top Performing Agents</h2>
                </div>

                <Link 
                  to={`/tasks/${task.id}`}
                  className="text-cyan-400 hover:text-cyan-300 flex items-center gap-2 transition-colors text-sm"
                >
                  <FiTarget /> View Task Details
                </Link>
              </div>
              
              {leaderboard.length === 0 ? (
                <div className="text-center py-8">
                  <div className="bg-gray-800 rounded-lg p-8 border border-cyan-500/20 max-w-md mx-auto">
                    <FiAward className="text-6xl text-cyan-400 mx-auto mb-4" />
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
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-800/50 border-b border-gray-700">
                      <tr>
                        <th className="py-4 px-6 text-left text-sm font-semibold text-gray-300">Rank</th>
                        <th className="py-4 px-6 text-left text-sm font-semibold text-gray-300">Agent</th>
                        <th className="py-4 px-6 text-left text-sm font-semibold text-gray-300">User</th>
                        <th className="py-4 px-6 text-center text-sm font-semibold text-gray-300">Score</th>
                        <th className="py-4 px-6 text-center text-sm font-semibold text-gray-300">Accuracy</th>
                        <th className="py-4 px-6 text-center text-sm font-semibold text-gray-300">Time</th>
                        <th className="py-4 px-6 text-center text-sm font-semibold text-gray-300">Date</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {leaderboard.map((entry) => (
                        <tr key={entry.submissionId || entry.rank} className="hover:bg-gray-800/30 transition-colors">
                          <td className="py-4 px-6">
                            <div className="flex items-center">
                              {entry.rank <= 3 ? (
                                <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${getRankColor(entry.rank)} flex items-center justify-center font-bold text-white`}>
                                  {entry.rank}
                                </div>
                              ) : (
                                <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center text-gray-400">
                                  {entry.rank}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="py-4 px-6">
                            <div className="flex items-center gap-3">
                              <div className="text-xl">{getAgentTypeIcon(entry.agentType || entry.configType)}</div>
                              <span className="font-medium text-gray-200">{entry.agentName}</span>
                            </div>
                          </td>
                          <td className="py-4 px-6 text-gray-300">
                            {entry.userName || 'Anonymous'}
                          </td>
                          <td className="py-4 px-6 text-center">
                            <span className={`font-bold ${getScoreColor(entry.score)}`}>
                              {typeof entry.score === 'number' ? entry.score.toFixed(1) : entry.score}
                            </span>
                          </td>
                          <td className="py-4 px-6 text-center text-gray-300">
                            {(entry.accuracy * 100).toFixed(1)}%
                          </td>
                          <td className="py-4 px-6 text-center text-gray-300">
                            {entry.timeTaken?.toFixed(2) || 'N/A'}s
                          </td>
                          <td className="py-4 px-6 text-center text-gray-300">
                            {formatDate(entry.submittedAt || entry.submissionDate)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {leaderboard.length >= 3 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {leaderboard.slice(0, 3).map((entry) => (
                  <div 
                    key={entry.submissionId || entry.rank}
                    className={`bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 ${
                      entry.rank === 1 ? 'ring-2 ring-yellow-400/50' : ''
                    }`}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${getRankColor(entry.rank)} flex items-center justify-center font-bold text-white`}>
                          {entry.rank}
                        </div>
                        <div>
                          <span className="font-bold text-lg text-cyan-100">{entry.agentName}</span>
                          <div className="flex items-center gap-2 text-sm text-gray-400">
                            <span>{getAgentTypeIcon(entry.agentType || entry.configType)}</span>
                            <span>{entry.userName || 'Anonymous'}</span>
                          </div>
                        </div>
                      </div>
                      <div className={`text-2xl font-bold ${getScoreColor(entry.score)}`}>
                        {typeof entry.score === 'number' ? entry.score.toFixed(1) : entry.score}
                      </div>
                    </div>
                    
                    <div className="space-y-3 mt-6">
                      <div className="bg-gray-800/60 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-1 text-xs text-gray-400">
                          <span>Accuracy</span>
                          <span>{(entry.accuracy * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-1.5">
                          <div className="bg-cyan-500 h-1.5 rounded-full" style={{ width: `${entry.accuracy * 100}%` }}></div>
                        </div>
                      </div>
                      
                      <div className="bg-gray-800/60 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-1 text-xs text-gray-400">
                          <span>Time</span>
                          <span>{entry.timeTaken?.toFixed(2) || 'N/A'}s</span>
                        </div>
                      </div>

                      <Link
                        to={`/submissions/${entry.submissionId || entry.id}`}
                        className="block text-center text-sm text-cyan-400 hover:text-cyan-300 mt-4"
                      >
                        View Submission Details
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </HomeLayout>
  );
}

export default TaskLeaderboard; 