import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiTarget, FiClock, FiUsers, FiAward, FiInfo } from 'react-icons/fi';
import axiosInstance from '../Helper/axiosInstance';
import HomeLayout from '../Layouts/HomeLayout';
import toast from 'react-hot-toast';

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [difficultyFilter, setDifficultyFilter] = useState('all');
  const [environmentFilter, setEnvironmentFilter] = useState('all');
  const [environments, setEnvironments] = useState([]);

  useEffect(() => {
    fetchTasks();
  }, []);

  useEffect(() => {
    // Apply filters when tasks, difficultyFilter, or environmentFilter changes
    if (tasks.length > 0) {
      let filtered = [...tasks];
      
      if (difficultyFilter !== 'all') {
        filtered = filtered.filter(task => 
          task.difficulty?.toLowerCase() === difficultyFilter.toLowerCase()
        );
      }
      
      if (environmentFilter !== 'all') {
        filtered = filtered.filter(task => 
          task.webArenaEnvironment?.toLowerCase() === environmentFilter.toLowerCase() ||
          task.category?.toLowerCase() === environmentFilter.toLowerCase()
        );
      }
      
      setFilteredTasks(filtered);
    }
  }, [tasks, difficultyFilter, environmentFilter]);

  const fetchTasks = async () => {
    try {
      const response = await axiosInstance.get('/tasks');
      const tasksData = response.data?.items || response.data || [];
      setTasks(tasksData);
      setFilteredTasks(tasksData);
      
      // Extract unique environments for filtering
      const uniqueEnvironments = [...new Set(tasksData.map(task => 
        task.webArenaEnvironment || task.category
      ))].filter(Boolean);
      
      setEnvironments(uniqueEnvironments);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      toast.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
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

  const getCategoryIcon = (category) => {
    if (!category) return '🎯';
    
    const categoryMap = {
      'omnizon': '🛒',
      'fly_united': '✈️',
      'gomail': '📧',
      'staynb': '🏨',
      'dashdish': '🍔',
      'gocalendar': '📅',
      'networkin': '👥',
      'udriver': '🚗',
      'topwork': '💼',
      'opendining': '🍽️',
      'zilloft': '🏠',
      'web_browsing': '🌐',
      'web-navigation': '🌐',
      'data-analysis': '📊',
      'nlp': '📝',
      'code-gen': '💻',
      'shopping': '🛒',
      'forum': '💬',
      'wiki': '📚',
    };
    
    return categoryMap[category.toLowerCase()] || '🎯';
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
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-5xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent mb-4">
              Benchmark Tasks
            </h1>
            <p className="text-xl text-cyan-200 max-w-3xl">
              Test your AI agents against our curated challenges. Each task is designed to evaluate 
              specific capabilities and performance metrics.
            </p>
          </div>
          
          {/* Filters */}
          <div className="mb-8 flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <span className="text-cyan-300">Difficulty:</span>
              <select
                value={difficultyFilter}
                onChange={(e) => setDifficultyFilter(e.target.value)}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
              >
                <option value="all">All Difficulties</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            
            {environments.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-cyan-300">Environment:</span>
                <select
                  value={environmentFilter}
                  onChange={(e) => setEnvironmentFilter(e.target.value)}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-cyan-500 focus:outline-none"
                >
                  <option value="all">All Environments</option>
                  {environments.map((env) => (
                    <option key={env} value={env}>{env}</option>
                  ))}
                </select>
              </div>
            )}
            
            <div className="ml-auto text-gray-400 text-sm">
              {filteredTasks.length} {filteredTasks.length === 1 ? 'task' : 'tasks'} found
            </div>
          </div>

          {filteredTasks.length === 0 ? (
            <div className="text-center py-16 bg-gray-800/50 rounded-xl border border-cyan-500/20">
              <FiInfo className="mx-auto text-6xl text-cyan-400 mb-4" />
              <h3 className="text-2xl font-bold text-cyan-100 mb-2">No Tasks Available</h3>
              <p className="text-cyan-200 max-w-md mx-auto mb-4">
                {tasks.length > 0 
                  ? 'No tasks match your current filters. Try changing your filter settings.'
                  : 'There are currently no benchmark tasks available. Please check back later.'}
              </p>
              {tasks.length > 0 && (
                <button
                  onClick={() => {
                    setDifficultyFilter('all');
                    setEnvironmentFilter('all');
                  }}
                  className="bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg transition"
                >
                  Clear Filters
                </button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {filteredTasks.map((task) => (
                <div 
                  key={task.id}
                  className="bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300 group"
                >
                  <div className="flex items-start gap-6">
                    <div className={`w-16 h-16 bg-gradient-to-br ${getDifficultyColor(task.difficulty)} rounded-xl flex items-center justify-center text-3xl`}>
                      {getCategoryIcon(task.webArenaEnvironment || task.category)}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <h3 className="text-2xl font-bold text-cyan-100 group-hover:text-cyan-300 transition-colors">
                          {task.title}
                        </h3>
                        <div className={`bg-gradient-to-r ${getDifficultyColor(task.difficulty)} text-white text-xs px-3 py-1 rounded-full font-bold`}>
                          {task.difficulty || 'Standard'}
                        </div>
                      </div>
                      <p className="text-gray-300 mt-3 mb-6">{task.description}</p>

                      <div className="flex flex-wrap gap-4 text-sm text-gray-400 mb-6">
                        <div className="flex items-center gap-1">
                          <FiTarget className="text-cyan-400" />
                          <span>{task.webArenaEnvironment || task.category || 'Standard'} Environment</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <FiClock className="text-yellow-400" />
                          <span>Est. {task.expectedCompletionTime || 300}s</span>
                        </div>
                      </div>

                      <div className="flex gap-3">
                        <Link 
                          to={`/tasks/${task.id}`}
                          className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white py-3 px-6 rounded-xl font-semibold transition-all duration-300 text-center"
                        >
                          View Details
                        </Link>
                        <Link 
                          to={`/tasks/${task.id}/leaderboard`}
                          className="bg-gray-700/50 hover:bg-gray-600/50 p-3 rounded-xl text-gray-300 hover:text-cyan-400 transition-all duration-300"
                        >
                          <FiAward className="text-xl" />
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </HomeLayout>
  );
}

export default Tasks; 