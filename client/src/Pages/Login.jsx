import { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { Link, useNavigate } from 'react-router-dom';
import HomeLayout from '../Layouts/HomeLayout';
import axiosInstance from '../Helper/axiosInstance';

function Login() {
  const navigate = useNavigate();

  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
  });

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      navigate('/');
    }
  }, [navigate]);

  function handleUserInput(e) {
    const { name, value } = e.target;
    setLoginData({
      ...loginData,
      [name]: value,
    });
  }

  async function onLogin(event) {
    event.preventDefault();
    if (!loginData.email || !loginData.password) {
      toast.error('Please fill all the details');
      return;
    }

    try {
      const response = await axiosInstance.post('/auth/login', loginData);
      const { access_token, refresh_token, role } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('role', role);

      toast.success('Login successful!');

      window.dispatchEvent(new Event('storage'));

      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed!');
    }
  }

  return (
    <HomeLayout>
      <div className="flex items-center justify-center min-h-[90vh] bg-gradient-to-br from-gray-900 via-blue-900/20 to-cyan-900/20 text-white">
        <form
          onSubmit={onLogin}
          className="flex flex-col justify-center gap-6 rounded-lg p-8 w-96 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg border border-cyan-500/20 shadow-2xl"
        >
          <h1 className="text-center text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">Login</h1>
          <div className="flex flex-col gap-2">
            <label htmlFor="email" className="font-semibold text-lg text-cyan-100">
              Email
            </label>
            <input
              type="email"
              name="email"
              id="email"
              placeholder="Enter your email..."
              className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white placeholder-gray-400 focus:border-cyan-500 focus:outline-none transition-colors"
              onChange={handleUserInput}
              value={loginData.email}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label htmlFor="password" className="font-semibold text-lg text-cyan-100">
              Password
            </label>
            <input
              type="password"
              name="password"
              id="password"
              placeholder="Enter your password..."
              className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white placeholder-gray-400 focus:border-cyan-500 focus:outline-none transition-colors"
              onChange={handleUserInput}
              value={loginData.password}
            />
          </div>
          <button type="submit" className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/25 mt-4">
            Login
          </button>
          <p className="text-center text-cyan-200 text-lg">
            Don't have an account?{' '}
            <Link to="/signup" className="text-cyan-400 hover:text-cyan-300 hover:underline">
              Signup
            </Link>
          </p>
        </form>
      </div>
    </HomeLayout>
  );
}

export default Login;
