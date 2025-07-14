import { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiCpu, FiTarget, FiClock, FiCheckCircle, FiXCircle, FiAlertCircle, FiDownload } from 'react-icons/fi';
import HomeLayout from '../Layouts/HomeLayout';
import axiosInstance from '../Helper/axiosInstance';
import toast from 'react-hot-toast';

function SubmissionDetails() {
  const { submissionId } = useParams();
  const navigate = useNavigate();
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, we would fetch submission details from the API
    // For now, let's use mock data
    setTimeout(() => {
      const mockSubmission = {
        id: submissionId,
        taskName: "Web Navigation Task",
        agentName: "GPT-4 Navigator",
        agentType: "gpt-4",
        status: "completed",
        score: 85,
        submittedAt: "2023-11-15T14:23:00Z",
        completedAt: "2023-11-15T14:28:35Z",
        metrics: {
          taskCompletion: 90,
          timeEfficiency: 80,
          accuracy: 85,
          resourceUsage: 75,
        },
        logs: [
          { timestamp: "14:23:05", message: "Agent initialized successfully", type: "info" },
          { timestamp: "14:23:10", message: "Accessing target website", type: "info" },
          { timestamp: "14:24:15", message: "Navigating form submission process", type: "info" },
          { timestamp: "14:25:30", message: "Extracting required information", type: "info" },
          { timestamp: "14:26:45", message: "Processing data extraction", type: "warning" },
          { timestamp: "14:27:20", message: "Validating results", type: "info" },
          { timestamp: "14:28:35", message: "Task completed successfully", type: "success" }
        ]
      };
      
      setSubmission(mockSubmission);
      setLoading(false);
    }, 800);
  }, [submissionId]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <FiCheckCircle className="text-green-400 text-xl" />;
      case 'failed': return <FiXCircle className="text-red-400 text-xl" />;
      case 'running': return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>;
      default: return <FiAlertCircle className="text-yellow-400 text-xl" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-400';
      case 'running': return 'text-blue-400';
      case 'failed': return 'text-red-400';
      default: return 'text-yellow-400';
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

  const getLogTypeColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'info': return 'text-cyan-300';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      default: return 'text-gray-300';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const calculateDuration = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffMs = end - start;
    const diffMins = Math.round(diffMs / 60000);
    const diffSecs = Math.round((diffMs % 60000) / 1000);
    return `${diffMins}m ${diffSecs}s`;
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
              to="/submissions"
              className="text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              <FiArrowLeft className="text-2xl" />
            </Link>
            <h1 className="text-4xl font-bold text-cyan-100">Submission Details</h1>
          </div>

          {submission && (
            <div className="space-y-8">
              <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20">
                <div className="flex justify-between items-start">
                  <div className="flex items-start gap-6">
                    <div className="bg-gray-800/80 p-4 rounded-xl">
                      <div className="text-4xl">{getAgentTypeIcon(submission.agentType)}</div>
                    </div>
                    
                    <div>
                      <div className="flex items-center gap-3">
                        <h2 className="text-3xl font-bold text-cyan-100">{submission.agentName}</h2>
                        <div className="flex items-center gap-2 bg-gray-800/50 py-1 px-3 rounded-full">
                          {getStatusIcon(submission.status)}
                          <span className={`font-medium ${getStatusColor(submission.status)}`}>
                            {submission.status.charAt(0).toUpperCase() + submission.status.slice(1)}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 mt-2 text-gray-400">
                        <FiTarget />
                        <span className="text-cyan-300">{submission.taskName}</span>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 text-sm">
                        <div className="flex flex-col">
                          <span className="text-gray-400">Submitted</span>
                          <span className="text-cyan-200 font-medium">{formatDate(submission.submittedAt)}</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-gray-400">Completed</span>
                          <span className="text-cyan-200 font-medium">
                            {submission.completedAt ? formatDate(submission.completedAt) : '—'}
                          </span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-gray-400">Duration</span>
                          <span className="text-cyan-200 font-medium">
                            {submission.completedAt ? calculateDuration(submission.submittedAt, submission.completedAt) : '—'}
                          </span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-gray-400">Score</span>
                          <span className="text-green-400 font-bold text-xl">
                            {submission.score !== null ? `${submission.score}%` : '—'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <button
                    className="bg-gray-800/50 hover:bg-gray-700/50 text-gray-300 hover:text-cyan-400 p-3 rounded-xl transition-colors"
                    title="Download Results"
                  >
                    <FiDownload className="text-lg" />
                  </button>
                </div>
              </div>

              <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20">
                <h3 className="text-2xl font-bold text-cyan-100 mb-6">Performance Metrics</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <div className="bg-gray-800/50 p-4 rounded-xl text-center">
                    <div className="text-3xl font-bold text-green-400">
                      {submission.metrics.taskCompletion}%
                    </div>
                    <div className="text-gray-400 mt-1">Task Completion</div>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-xl text-center">
                    <div className="text-3xl font-bold text-cyan-400">
                      {submission.metrics.timeEfficiency}%
                    </div>
                    <div className="text-gray-400 mt-1">Time Efficiency</div>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-xl text-center">
                    <div className="text-3xl font-bold text-yellow-400">
                      {submission.metrics.accuracy}%
                    </div>
                    <div className="text-gray-400 mt-1">Accuracy</div>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-xl text-center">
                    <div className="text-3xl font-bold text-purple-400">
                      {submission.metrics.resourceUsage}%
                    </div>
                    <div className="text-gray-400 mt-1">Resource Usage</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Task Completion</span>
                      <span className="text-green-400">{submission.metrics.taskCompletion}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${submission.metrics.taskCompletion}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Time Efficiency</span>
                      <span className="text-cyan-400">{submission.metrics.timeEfficiency}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${submission.metrics.timeEfficiency}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Accuracy</span>
                      <span className="text-yellow-400">{submission.metrics.accuracy}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-yellow-500 to-orange-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${submission.metrics.accuracy}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-300">Resource Usage</span>
                      <span className="text-purple-400">{submission.metrics.resourceUsage}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-purple-500 to-violet-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${submission.metrics.resourceUsage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20">
                <h3 className="text-2xl font-bold text-cyan-100 mb-6">Execution Logs</h3>
                
                <div className="space-y-2">
                  {submission.logs.map((log, index) => (
                    <div key={index} className="bg-gray-800/50 p-3 rounded-lg flex items-start gap-3">
                      <div className="text-gray-500 font-mono whitespace-nowrap">{log.timestamp}</div>
                      <div className={`${getLogTypeColor(log.type)}`}>{log.message}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Link 
                  to={`/tasks/${1}`}
                  className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 flex items-center justify-between group hover:border-cyan-400/40 transition-all duration-300"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center">
                      <FiTarget className="text-xl text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-cyan-100">View Task Details</h3>
                      <p className="text-gray-400">{submission.taskName}</p>
                    </div>
                  </div>
                  <div className="group-hover:translate-x-2 transition-transform">→</div>
                </Link>

                <Link 
                  to={`/agents/${1}`}
                  className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-6 rounded-2xl border border-cyan-500/20 flex items-center justify-between group hover:border-cyan-400/40 transition-all duration-300"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl flex items-center justify-center">
                      <FiCpu className="text-xl text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-cyan-100">View Agent Details</h3>
                      <p className="text-gray-400">{submission.agentName}</p>
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

export default SubmissionDetails; 