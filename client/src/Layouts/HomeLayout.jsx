import React, { useState, useEffect } from 'react';
import { FiMenu, FiX, FiUser, FiCpu, FiTrendingUp, FiAward, FiSettings, FiZap } from 'react-icons/fi';
import { Link, useNavigate, useLocation } from 'react-router-dom';

function HomeLayout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access_token'));
  const [userRole, setUserRole] = useState(localStorage.getItem('role') || '');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const handleStorageChange = () => {
      setIsLoggedIn(!!localStorage.getItem('access_token'));
      setUserRole(localStorage.getItem('role') || '');
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const handleLogout = async (e) => {
    e.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    localStorage.removeItem('email');

    window.dispatchEvent(new Event('storage'));
    setIsMenuOpen(false);
    navigate('/login');
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  const isActivePath = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  // Helper function to check if user is admin
  const isAdmin = () => {
    return userRole === 'ADMIN' || userRole === 'UserRole.ADMIN';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/10 to-cyan-900/10">
      <nav className="bg-gray-800/80 backdrop-blur-lg border-b border-cyan-500/20 px-4 py-4 sticky top-0 z-30 shadow-xl">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-6">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-cyan-400 hover:text-cyan-300 transition-all duration-300 p-2 rounded-lg hover:bg-cyan-400/10 md:hidden"
            >
              {isMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>

            <Link
              to="/"
              className="flex items-center gap-3 group"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <FiZap className="text-white text-xl" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                AgentArena
              </span>
            </Link>
          </div>

          <div className="hidden md:flex items-center gap-2">
            {isLoggedIn && (
              <>
                <Link
                  to="/agents"
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all duration-300 ${
                    isActivePath('/agents') 
                      ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/20' 
                      : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                  }`}
                >
                  <FiCpu size={18} /> Agents
                </Link>

                <Link
                  to="/playground"
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all duration-300 ${
                    isActivePath('/playground') 
                      ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/20' 
                      : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                  }`}
                >
                  <FiZap size={18} /> Playground
                </Link>
              </>
            )}

            <Link
              to="/leaderboard"
              className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all duration-300 ${
                isActivePath('/leaderboard') 
                  ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/20' 
                  : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
              }`}
            >
              <FiAward size={18} /> Leaderboard
            </Link>

            {isLoggedIn ? (
              <div className="flex items-center gap-2 ml-4">
                <Link
                  to="/profile"
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all duration-300 ${
                    isActivePath('/profile') 
                      ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/20' 
                      : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                  }`}
                >
                  <FiUser size={18} /> Profile
                </Link>

                {isAdmin() && (
                  <Link
                    to="/admin/dashboard"
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all duration-300 ${
                      isActivePath('/admin') 
                        ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/20' 
                        : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                    }`}
                  >
                    <FiSettings size={18} /> Admin
                  </Link>
                )}

                <button
                  onClick={handleLogout}
                  className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-6 py-2 rounded-xl font-semibold transition-all duration-300 ml-2 hover:shadow-lg hover:shadow-red-500/25"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3 ml-4">
                <Link 
                  to="/login" 
                  className="text-cyan-400 hover:text-cyan-300 px-6 py-2 rounded-xl font-semibold transition-all duration-300 hover:bg-cyan-400/10"
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white px-6 py-2 rounded-xl font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/25"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>

      {isMenuOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden" onClick={closeMenu}>
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 w-80 h-full border-r border-cyan-500/20 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b border-gray-700/50">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center">
                  <FiZap className="text-white text-xl" />
                </div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                  AgentArena
                </h2>
              </div>
              <p className="text-cyan-300 text-sm mt-2">AI Agent Benchmarking Platform</p>
            </div>

            <nav className="p-6 space-y-3">
              <Link
                to="/"
                onClick={closeMenu}
                className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 ${
                  isActivePath('/') && location.pathname === '/'
                    ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/10'
                    : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                }`}
              >
                <span className="text-xl">🏠</span>
                <span className="font-semibold">Home</span>
              </Link>

              {isLoggedIn && (
                <>
                  <Link
                    to="/agents"
                    onClick={closeMenu}
                    className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 ${
                      isActivePath('/agents') 
                        ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/10' 
                        : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                    }`}
                  >
                    <FiCpu size={20} />
                    <span className="font-semibold">Agent Hub</span>
                  </Link>

                  <Link
                    to="/playground"
                    onClick={closeMenu}
                    className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 ${
                      isActivePath('/playground') 
                        ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/10' 
                        : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                    }`}
                  >
                    <FiZap size={20} />
                    <span className="font-semibold">Playground</span>
                  </Link>
                </>
              )}

              <Link
                to="/leaderboard"
                onClick={closeMenu}
                className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 ${
                  isActivePath('/leaderboard') 
                    ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/10' 
                    : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                }`}
              >
                <FiAward size={20} />
                <span className="font-semibold">Leaderboard</span>
              </Link>

              {isLoggedIn ? (
                <>
                  <Link
                    to="/profile"
                    onClick={closeMenu}
                    className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 ${
                      isActivePath('/profile') 
                        ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/10' 
                        : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                    }`}
                  >
                    <FiUser size={20} />
                    <span className="font-semibold">Profile</span>
                  </Link>

                  {isAdmin() && (
                    <Link
                      to="/admin/dashboard"
                      onClick={closeMenu}
                      className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 ${
                        isActivePath('/admin') 
                          ? 'text-cyan-400 bg-cyan-400/20 shadow-lg shadow-cyan-400/10' 
                          : 'text-gray-300 hover:text-cyan-400 hover:bg-cyan-400/10'
                      }`}
                    >
                      <FiSettings size={20} />
                      <span className="font-semibold">Admin Dashboard</span>
                    </Link>
                  )}

                  <div className="pt-6 border-t border-gray-700/50 mt-6">
                    <button
                      onClick={handleLogout}
                      className="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-4 py-3 rounded-xl font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-red-500/25"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <div className="pt-6 border-t border-gray-700/50 mt-6 space-y-3">
                  <Link
                    to="/login"
                    onClick={closeMenu}
                    className="block w-full text-center text-cyan-400 hover:text-cyan-300 px-4 py-3 border border-cyan-500/50 rounded-xl transition-all duration-300 hover:bg-cyan-400/10 font-semibold"
                  >
                    Login
                  </Link>
                  <Link
                    to="/signup"
                    onClick={closeMenu}
                    className="block w-full text-center bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white px-4 py-3 rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/25 font-semibold"
                  >
                    Sign Up
                  </Link>
                </div>
              )}
            </nav>
          </div>
        </div>
      )}

      <main className="min-h-screen">{children}</main>
    </div>
  );
}

export default HomeLayout;
