import { Link } from 'react-router-dom';
import { FiCpu, FiTarget, FiTrendingUp, FiUsers, FiZap, FiShield } from 'react-icons/fi';
import HomeLayout from '../Layouts/HomeLayout';

function HomePage() {
  const features = [
    {
      icon: <FiCpu className="text-3xl" />,
      title: "AI Agent Management",
      description: "Create, configure, and manage multiple AI agents with different capabilities and models."
    },
    {
      icon: <FiTarget className="text-3xl" />,
      title: "Performance Benchmarking", 
      description: "Comprehensive evaluation metrics and performance analysis for your AI agents."
    },
    {
      icon: <FiTrendingUp className="text-3xl" />,
      title: "Advanced Analytics",
      description: "Deep insights into agent behavior, efficiency patterns, and optimization opportunities."
    },
    {
      icon: <FiZap className="text-3xl" />,
      title: "Real-time Testing",
      description: "Instant agent testing with live performance monitoring and detailed execution logs."
    },
    {
      icon: <FiShield className="text-3xl" />,
      title: "Secure Evaluation",
      description: "Safe testing environment with isolated execution and comprehensive security measures."
    },
    {
      icon: <FiUsers className="text-3xl" />,
      title: "Competitive Leaderboards",
      description: "Compare your agents against others and track performance improvements over time."
    }
  ];

  return (
    <HomeLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-cyan-900">
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/10 to-blue-600/10 animate-pulse"></div>
          
          <div className="relative min-h-[100vh] flex flex-col lg:flex-row items-center justify-center gap-12 px-8 lg:px-16 text-white">
            <div className="lg:w-1/2 text-center lg:text-left space-y-8">
              <div className="space-y-4">
                <h1 className="text-6xl lg:text-7xl font-extrabold leading-tight">
                  <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-600 bg-clip-text text-transparent">
                    AgentArena
                  </span>
                </h1>
                <h2 className="text-3xl lg:text-4xl font-bold text-cyan-100 mb-6">
                  AI Agent Benchmarking Platform
                </h2>
                <p className="text-xl text-cyan-200 leading-relaxed max-w-2xl">
                  The ultimate platform for evaluating, benchmarking, and optimizing AI agents. 
                  Deploy advanced testing scenarios and measure performance with precision.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-6 mt-12">
                <Link to="/agents">
                  <button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 px-10 py-4 rounded-xl font-bold text-lg transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/25">
                    Start Benchmarking
                  </button>
                </Link>
                <Link to="/leaderboard">
                  <button className="border-2 border-cyan-400 hover:border-cyan-300 px-10 py-4 rounded-xl font-bold text-lg transition-all duration-300 hover:bg-cyan-400/20 hover:shadow-xl hover:shadow-cyan-400/25">
                    View Leaderboard
                  </button>
                </Link>
              </div>

              <div className="grid grid-cols-3 gap-6 mt-12 text-center">
                <div className="space-y-2">
                  <div className="text-3xl font-bold text-cyan-400">500+</div>
                  <div className="text-sm text-cyan-200">Agents Tested</div>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl font-bold text-blue-400">12</div>
                  <div className="text-sm text-cyan-200">Benchmark Tasks</div>
                </div>
                <div className="space-y-2">
                  <div className="text-3xl font-bold text-indigo-400">99.9%</div>
                  <div className="text-sm text-cyan-200">Uptime</div>
                </div>
              </div>
            </div>

            <div className="lg:w-1/2 flex justify-center">
              <div className="relative">
                <div className="w-96 h-96 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 backdrop-blur-lg border border-cyan-400/30 flex items-center justify-center shadow-2xl">
                  <div className="w-80 h-80 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-transparent to-black/20"></div>
                    <div className="relative z-10 text-center space-y-4">
                      <FiCpu className="text-6xl text-white mx-auto animate-pulse" />
                      <div className="text-white font-bold text-xl">AgentArena</div>
                      <div className="text-cyan-100 text-sm">AI Benchmarking</div>
                    </div>
                  </div>
                </div>
                <div className="absolute -top-4 -right-4 w-24 h-24 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-2xl animate-bounce">
                  ⚡
                </div>
                <div className="absolute -bottom-4 -left-4 w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center text-xl animate-pulse">
                  🎯
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="py-20 px-8 lg:px-16">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h3 className="text-4xl font-bold text-cyan-100 mb-6">
                Powerful Benchmarking Features
              </h3>
              <p className="text-xl text-cyan-200 max-w-3xl mx-auto">
                Everything you need to evaluate, compare, and optimize your AI agents in one comprehensive platform.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <div 
                  key={index}
                  className="bg-gray-800/50 backdrop-blur-lg p-8 rounded-2xl border border-cyan-500/20 hover:border-cyan-400/40 transition-all duration-300 hover:transform hover:scale-105 hover:shadow-xl hover:shadow-cyan-500/10"
                >
                  <div className="text-cyan-400 mb-4">
                    {feature.icon}
                  </div>
                  <h4 className="text-xl font-bold text-cyan-100 mb-3">
                    {feature.title}
                  </h4>
                  <p className="text-cyan-200 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="py-20 px-8 lg:px-16 bg-gradient-to-r from-cyan-900/30 to-blue-900/30">
          <div className="max-w-4xl mx-auto text-center">
            <h3 className="text-4xl font-bold text-cyan-100 mb-6">
              Ready to Benchmark Your AI Agents?
            </h3>
            <p className="text-xl text-cyan-200 mb-8">
              Join the future of AI agent evaluation and optimization.
            </p>
            <Link to="/agents/create">
              <button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 px-12 py-4 rounded-xl font-bold text-xl transition-all duration-300 transform hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/25">
                Create Your First Agent
              </button>
            </Link>
          </div>
        </div>
      </div>
    </HomeLayout>
  );
}

export default HomePage;
