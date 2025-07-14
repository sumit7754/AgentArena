import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { FiPlay, FiCpu, FiSettings, FiZap, FiTarget, FiMonitor, FiRefreshCw, FiKey, FiLock } from 'react-icons/fi';
import HomeLayout from '../Layouts/HomeLayout';
import axiosInstance from '../Helper/axiosInstance';
import PlaygroundHealthCheck from '../components/PlaygroundHealthCheck';

function Playground() {
  const location = useLocation();
  const navigate = useNavigate();
  const [agents, setAgents] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [llmApiKey, setLlmApiKey] = useState('');
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [healthStatus, setHealthStatus] = useState({
    mockMode: true,
    supportedProviders: []
  });

  useEffect(() => {
    fetchData();
    
    // Check if agent was pre-selected from another page
    const preselectedAgent = location.state?.preselectedAgent;
    const preselectedTask = location.state?.preselectedTask;
    
    if (preselectedAgent) {
      setSelectedAgent(preselectedAgent);
      // Check for stored API key
      const storedApiKey = sessionStorage.getItem(`llm_api_key_${preselectedAgent.id}`);
      if (storedApiKey) {
        setLlmApiKey(storedApiKey);
      }
    }
    
    if (preselectedTask) {
      setSelectedTask(preselectedTask);
    }
  }, [location.state]);

  const fetchData = async () => {
    try {
      const [agentsResponse, tasksResponse, healthResponse] = await Promise.all([
        axiosInstance.get('/agents'),
        axiosInstance.get('/tasks'),
        axiosInstance.get('/playground/health')
      ]);
      
      const agentsData = agentsResponse.data.agents || agentsResponse.data.items || [];
      const tasksData = tasksResponse.data.items || tasksResponse.data || [];
      
      setAgents(agentsData);
      setTasks(tasksData);
      setHealthStatus({
        mockMode: healthResponse.data.mock_mode || true,
        supportedProviders: healthResponse.data.supported_providers || []
      });
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load agents or tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    // Check for stored API key when agent is selected
    const storedApiKey = sessionStorage.getItem(`llm_api_key_${agent.id}`);
    if (storedApiKey) {
      setLlmApiKey(storedApiKey);
    } else {
      setLlmApiKey('');
    }
  };

  const handleApiKeySubmit = (e) => {
    e.preventDefault();
    if (!llmApiKey.trim()) {
      toast.error('Please enter an API key');
      return;
    }
    
    // Store API key in session storage
    if (selectedAgent) {
      sessionStorage.setItem(`llm_api_key_${selectedAgent.id}`, llmApiKey);
    }
    
    setShowApiKeyModal(false);
    runBenchmark(); // Run benchmark after API key is provided
  };

  const runBenchmark = async () => {
    if (!selectedAgent) {
      toast.error('Please select an agent first');
      return;
    }
    
    if (!selectedTask) {
      toast.error('Please select a task first');
      return;
    }
    
    // Check if we have an API key for real LLM agents
    if (selectedAgent.configType === 'real' && !healthStatus.mockMode && !llmApiKey) {
      setShowApiKeyModal(true);
      return;
    }

    setIsRunning(true);
    setResult(null);

    try {
      const benchmarkData = {
        agent_id: selectedAgent.id,
        task_id: selectedTask.id,
        run_config: {
          llm_api_key: llmApiKey // Send the API key with the request (backend won't store it)
        }
      };

      const response = await axiosInstance.post('/submissions', benchmarkData);
      setResult(response.data);
      toast.success('Benchmark evaluation initiated!');
      
      // Poll for results if the submission is pending
      if (response.data.status === 'pending' || response.data.status === 'processing') {
        pollSubmissionStatus(response.data.id);
      }
    } catch (error) {
      console.error('Benchmark execution error:', error);
      toast.error(error.response?.data?.detail || 'Failed to run benchmark');
      setResult({
        success: false,
        error: error.response?.data?.detail || 'Execution failed',
        timeTaken: 0,
      });
      setIsRunning(false);
    }
  };
  
  const pollSubmissionStatus = async (submissionId) => {
    let attempts = 0;
    const maxAttempts = 30; // 30 x 2 seconds = 1 minute max
    
    const checkStatus = async () => {
      if (attempts >= maxAttempts) {
        setIsRunning(false);
        toast.error('Benchmark is taking longer than expected. Please check results page.');
        return;
      }
      
      try {
        const response = await axiosInstance.get(`/submissions/${submissionId}`);
        const submission = response.data;
        
        if (submission.status === 'completed' || submission.status === 'failed') {
          setResult(submission);
          setIsRunning(false);
          toast.success('Benchmark evaluation completed!');
          return;
        }
        
        // Continue polling
        attempts++;
        setTimeout(checkStatus, 2000);
      } catch (error) {
        console.error('Error polling submission status:', error);
        setIsRunning(false);
      }
    };
    
    setTimeout(checkStatus, 2000);
  };

  const getTaskTypeColor = (taskType) => {
    switch (taskType?.toLowerCase()) {
      case 'easy': return 'text-green-400 bg-green-400/20';
      case 'medium': return 'text-yellow-400 bg-yellow-400/20';
      case 'hard': return 'text-red-400 bg-red-400/20';
      default: return 'text-blue-400 bg-blue-400/20';
    }
  };

  if (loading) {
    return (
      <HomeLayout>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-cyan-900/20 flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-cyan-400"></div>
        </div>
      </HomeLayout>
    );
  }

  return (
    <HomeLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-cyan-900/20 text-white">
        <div className="container mx-auto px-6 py-8">
          <div className="mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent mb-4">
              Agent Playground
            </h1>
            <p className="text-xl text-cyan-200">
              Test your AI agents against benchmark tasks
            </p>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Configuration Panel */}
            <div className="xl:col-span-2 space-y-6">
              {/* Agent Selection */}
              <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-cyan-500/20">
                <h3 className="text-xl font-bold text-cyan-100 mb-4 flex items-center gap-2">
                  <FiCpu className="text-cyan-400" />
                  Select Agent
                </h3>
                {agents.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-cyan-200 mb-4">No agents available</p>
                    <button
                      onClick={() => navigate('/agents/create')}
                      className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 px-6 py-3 rounded-xl font-semibold transition-all duration-300"
                    >
                      Create Your First Agent
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {agents.map((agent) => (
                      <div
                        key={agent.id}
                        className={`p-4 rounded-xl border cursor-pointer transition-all duration-300 ${
                          selectedAgent?.id === agent.id
                            ? 'border-cyan-400 bg-cyan-400/10 shadow-lg shadow-cyan-400/20'
                            : 'border-gray-600 hover:border-cyan-500/50 hover:bg-gray-700/50'
                        }`}
                        onClick={() => handleAgentSelect(agent)}
                      >
                        <h4 className="font-semibold text-white mb-2">{agent.name}</h4>
                        <p className="text-cyan-200 text-sm mb-2">{agent.description || 'No description available'}</p>
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

              {/* Task Selection */}
              <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-cyan-500/20">
                <h3 className="text-xl font-bold text-cyan-100 mb-4 flex items-center gap-2">
                  <FiTarget className="text-cyan-400" />
                  Select Task
                </h3>
                {tasks.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-cyan-200">No benchmark tasks available</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {tasks.map((task) => (
                      <div
                        key={task.id}
                        className={`p-4 rounded-xl border cursor-pointer transition-all duration-300 ${
                          selectedTask?.id === task.id
                            ? 'border-cyan-400 bg-cyan-400/10 shadow-lg shadow-cyan-400/20'
                            : 'border-gray-600 hover:border-cyan-500/50 hover:bg-gray-700/50'
                        }`}
                        onClick={() => setSelectedTask(task)}
                      >
                        <h4 className="font-semibold text-white mb-2">{task.title}</h4>
                        <p className="text-cyan-200 text-sm mb-3">{task.description || 'No description available'}</p>
                        <div className="flex items-center justify-between">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getTaskTypeColor(task.difficulty)}`}>
                            {task.difficulty || 'Standard'}
                          </span>
                          <span className="text-xs text-gray-400">
                            {task.webArenaEnvironment || task.category || 'Standard'} Environment
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Execution Options */}
              <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-cyan-500/20">
                <h3 className="text-xl font-bold text-cyan-100 mb-4 flex items-center gap-2">
                  <FiSettings className="text-cyan-400" />
                  Evaluation Options
                </h3>
                <div className="grid grid-cols-1 gap-4">
                  <PlaygroundHealthCheck />
                  
                  {/* API Key Input (visible if agent selected is real) */}
                  {selectedAgent && selectedAgent.configType === 'real' && !healthStatus.mockMode && (
                    <div className="mt-4 p-3 bg-gray-700/50 border border-amber-500/30 rounded-lg">
                      <div className="flex items-center gap-2 text-sm mb-3">
                        <FiLock className="text-amber-400" />
                        <span className="text-amber-300">API Key Required</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="relative flex-grow">
                          <input
                            type="password"
                            value={llmApiKey}
                            onChange={(e) => setLlmApiKey(e.target.value)}
                            placeholder={llmApiKey ? '••••••••••••••••••••••••••' : 'Enter your LLM API key'}
                            className="w-full bg-gray-600/50 border border-gray-500 p-3 pr-10 rounded-lg text-white"
                          />
                          <FiKey className="absolute right-3 top-3 text-gray-400" />
                        </div>
                        <button
                          onClick={() => setLlmApiKey('')}
                          className="text-xs bg-gray-600/50 hover:bg-gray-500/50 text-gray-300 py-2 px-3 rounded"
                        >
                          Clear
                        </button>
                      </div>
                      <p className="text-xs text-amber-200/80 mt-2">
                        Your API key is never stored on our servers. It is only used for this evaluation.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Execution Panel */}
            <div className="space-y-6">
              {/* Run Button */}
              <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-cyan-500/20">
                <button
                  onClick={runBenchmark}
                  disabled={!selectedAgent || !selectedTask || isRunning}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white py-4 rounded-xl font-bold text-lg transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/25 flex items-center justify-center gap-2"
                >
                  {isRunning ? (
                    <>
                      <FiRefreshCw className="animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <FiPlay />
                      Run Benchmark
                    </>
                  )}
                </button>
              </div>

              {/* Results Panel */}
              {result && (
                <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-cyan-500/20">
                  <h3 className="text-xl font-bold text-cyan-100 mb-4 flex items-center gap-2">
                    <FiMonitor className="text-cyan-400" />
                    Evaluation Results
                  </h3>
                  
                  <div className="space-y-4">
                    <div className={`p-4 rounded-lg ${result.matched || result.success ? 'bg-green-500/20 border border-green-500/30' : 'bg-red-500/20 border border-red-500/30'}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">{result.matched || result.success ? '✅' : '❌'}</span>
                        <span className="font-semibold text-white">
                          {result.matched || result.success ? 'Passed' : 'Failed'}
                        </span>
                      </div>
                      {result.error && (
                        <p className="text-red-300 text-sm">{result.error}</p>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gray-700/50 p-3 rounded-lg">
                        <p className="text-cyan-200 text-sm">Time Taken</p>
                        <p className="text-white font-semibold">
                          {result.timeTaken?.toFixed(2) || result.execution_time_seconds?.toFixed(2) || 0}s
                        </p>
                      </div>
                      {(result.tokensUsed || result.tokens_used) && (
                        <div className="bg-gray-700/50 p-3 rounded-lg">
                          <p className="text-cyan-200 text-sm">Tokens Used</p>
                          <p className="text-white font-semibold">{result.tokensUsed || result.tokens_used}</p>
                        </div>
                      )}
                    </div>

                    {(result.accuracy !== undefined || result.success_rate !== undefined) && (
                      <div className="bg-gray-700/50 p-3 rounded-lg">
                        <p className="text-cyan-200 text-sm">Accuracy</p>
                        <p className="text-white font-semibold">
                          {(result.accuracy !== undefined ? result.accuracy * 100 : result.success_rate * 100).toFixed(1)}%
                        </p>
                      </div>
                    )}

                    {/* Task Input and Response */}
                    {(result.taskPrompt || result.task_prompt) && (
                      <div className="bg-gray-900/50 p-4 rounded-lg">
                        <p className="text-cyan-200 text-sm mb-2">Task Prompt</p>
                        <pre className="text-xs text-gray-300 overflow-x-auto bg-gray-800/50 p-3 rounded">
                          {result.taskPrompt || result.task_prompt}
                        </pre>
                      </div>
                    )}

                    {(result.agentResponse || result.agent_response) && (
                      <div className="bg-gray-900/50 p-4 rounded-lg">
                        <p className="text-cyan-200 text-sm mb-2">Agent Response</p>
                        <pre className="text-xs text-gray-300 overflow-x-auto bg-gray-800/50 p-3 rounded">
                          {result.agentResponse || result.agent_response}
                        </pre>
                      </div>
                    )}

                    {(result.expectedOutput || result.expected_output) && (
                      <div className="bg-gray-900/50 p-4 rounded-lg">
                        <p className="text-cyan-200 text-sm mb-2">Expected Output</p>
                        <pre className="text-xs text-gray-300 overflow-x-auto bg-gray-800/50 p-3 rounded">
                          {result.expectedOutput || result.expected_output}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* API Key Modal */}
      {showApiKeyModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full shadow-xl border border-cyan-500/30">
            <h3 className="text-xl font-bold text-cyan-100 mb-4 flex items-center gap-2">
              <FiKey className="text-cyan-400" />
              API Key Required
            </h3>
            <p className="text-gray-300 mb-6">
              To run this benchmark, please provide your LLM API key. The key will only be used for this evaluation and won't be stored on our servers.
            </p>
            <form onSubmit={handleApiKeySubmit}>
              <div className="mb-4">
                <input
                  type="password"
                  value={llmApiKey}
                  onChange={(e) => setLlmApiKey(e.target.value)}
                  placeholder="Enter your LLM API key"
                  className="w-full bg-gray-700 border border-gray-600 p-3 rounded-lg text-white"
                  autoFocus
                />
              </div>
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowApiKeyModal(false)}
                  className="px-4 py-2 border border-gray-500 text-gray-300 rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded hover:from-cyan-600 hover:to-blue-700"
                >
                  Submit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </HomeLayout>
  );
}

export default Playground;