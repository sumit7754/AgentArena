import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiCpu, FiCheck, FiX, FiActivity } from 'react-icons/fi';
import HomeLayout from '../Layouts/HomeLayout';
import axiosInstance from '../Helper/axiosInstance';
import toast from 'react-hot-toast';

function Submissions() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, we would fetch from the API
    // For now, let's use mock data
    setTimeout(() => {
      const mockSubmissions = [
        {
          id: "sub1",
          taskName: "Web Navigation Task",
          agentName: "GPT-4 Navigator",
          agentType: "gpt-4",
          status: "completed",
          score: 85,
          submittedAt: "2023-11-15T14:23:00Z"
        },
        {
          id: "sub2",
          taskName: "Data Analysis Challenge",
          agentName: "Claude Analyst",
          agentType: "claude-3",
          status: "completed",
          score: 92,
          submittedAt: "2023-11-12T09:45:00Z"
        },
        {
          id: "sub3",
          taskName: "Text Summarization",
          agentName: "Custom Parser",
          agentType: "custom",
          status: "failed",
          score: 0,
          submittedAt: "2023-11-10T16:30:00Z"
        },
        {
          id: "sub4",
          taskName: "Web Navigation Task",
          agentName: "GPT-3.5 Navigator",
          agentType: "gpt-3.5-turbo",
          status: "running",
          score: null,
          submittedAt: "2023-11-18T08:15:00Z"
        }
      ];
      
      setSubmissions(mockSubmissions);
      setLoading(false);
    }, 800);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'running': return 'bg-blue-500 animate-pulse';
      case 'failed': return 'bg-red-500';
      case 'pending': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'running': return 'Running';
      case 'failed': return 'Failed';
      case 'pending': return 'Pending';
      default: return 'Unknown';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 75) return 'text-cyan-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
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
          <div className="flex justify-between items-center mb-12">
            <div className="space-y-4">
              <h1 className="text-4xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                Agent Submissions
              </h1>
              <p className="text-xl text-cyan-200">Track your agent benchmark submissions and results</p>
              <div className="flex items-center gap-6 text-sm text-cyan-300">
                <div className="flex items-center gap-2">
                  <FiActivity className="text-cyan-400" />
                  <span>{submissions.length} Submissions</span>
                </div>
              </div>
            </div>
          </div>

          {submissions.length === 0 ? (
            <div className="text-center py-16 bg-gray-800/50 rounded-2xl border border-gray-700">
              <div className="w-20 h-20 mx-auto bg-gray-700/50 rounded-full flex items-center justify-center mb-4">
                <FiActivity className="text-3xl text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-300 mb-2">No Submissions Yet</h3>
              <p className="text-gray-400 mb-6">You haven't submitted any agents for benchmarking yet.</p>
              <Link 
                to="/tasks"
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white py-2 px-6 rounded-xl font-semibold inline-flex items-center gap-2"
              >
                <FiCpu /> Submit an Agent
              </Link>
            </div>
          ) : (
            <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg rounded-2xl border border-cyan-500/20 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-800/50 border-b border-gray-700">
                    <tr>
                      <th className="py-4 px-6 text-left text-sm font-semibold text-gray-300">Task</th>
                      <th className="py-4 px-6 text-left text-sm font-semibold text-gray-300">Agent</th>
                      <th className="py-4 px-6 text-center text-sm font-semibold text-gray-300">Status</th>
                      <th className="py-4 px-6 text-center text-sm font-semibold text-gray-300">Score</th>
                      <th className="py-4 px-6 text-left text-sm font-semibold text-gray-300">Submitted</th>
                      <th className="py-4 px-6 text-center text-sm font-semibold text-gray-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {submissions.map((submission) => (
                      <tr key={submission.id} className="hover:bg-gray-800/30 transition-colors">
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <span className="font-medium text-cyan-300">{submission.taskName}</span>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <div className="flex items-center gap-3">
                            <div className="text-xl">{getAgentTypeIcon(submission.agentType)}</div>
                            <span className="font-medium text-gray-200">{submission.agentName}</span>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <div className="flex items-center justify-center gap-2">
                            <div className={`w-3 h-3 rounded-full ${getStatusColor(submission.status)}`}></div>
                            <span>{getStatusText(submission.status)}</span>
                          </div>
                        </td>
                        <td className="py-4 px-6 text-center">
                          {submission.score !== null ? (
                            <span className={`font-bold ${getScoreColor(submission.score)}`}>
                              {submission.score}%
                            </span>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="py-4 px-6 text-gray-300 text-sm">
                          <div className="flex items-center gap-2">
                            <FiClock className="text-gray-400" />
                            <span>{formatDate(submission.submittedAt)}</span>
                          </div>
                        </td>
                        <td className="py-4 px-6">
                          <div className="flex items-center justify-center">
                            <Link 
                              to={`/submissions/${submission.id}`}
                              className="bg-gray-700 hover:bg-gray-600 text-gray-200 py-1 px-4 rounded-lg text-sm transition-colors"
                            >
                              Details
                            </Link>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </HomeLayout>
  );
}

export default Submissions; 