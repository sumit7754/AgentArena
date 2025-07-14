import { useEffect, useState } from 'react';
import { toast } from 'react-hot-toast';
import { Link, useNavigate } from 'react-router-dom';
import HomeLayout from '../Layouts/HomeLayout';
import axiosInstance from '../Helper/axiosInstance';

function Signup() {
  const navigate = useNavigate();

  const [signupData, setSignupData] = useState({
    username: '',
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
    setSignupData({
      ...signupData,
      [name]: value,
    });
  }

  async function createNewAccount(event) {
    event.preventDefault();

    if (!signupData.username || !signupData.email || !signupData.password) {
      toast.error('Please fill all the details');
      return;
    }
    if (signupData.username.length < 5) {
      toast.error('Username should be at least 5 characters');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(signupData.email)) {
      toast.error('Invalid email format');
      return;
    }
    if (!/^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-zA-Z]).{6,16}$/.test(signupData.password)) {
      toast.error('Password must be 6-16 characters with a number & special character');
      return;
    }

    try {
      const response = axiosInstance.post('/auth/register', signupData);

      toast.promise(response, {
        loading: 'Creating your account...',
        success: (res) => {
          const { access_token, refresh_token, role } = res.data;

          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          localStorage.setItem('role', role);

          navigate('/');
          return 'Account created successfully!';
        },
        error: (error) => error.response?.data?.detail || 'Failed to create account',
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Something went wrong');
    }
  }

  return (
    <HomeLayout>
      <div className="flex items-center justify-center min-h-[90vh] bg-gradient-to-br from-gray-900 via-blue-900/20 to-cyan-900/20 text-white">
        <form
          onSubmit={createNewAccount}
          className="flex flex-col justify-center gap-6 rounded-lg p-8 w-96 bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-lg border border-cyan-500/20 shadow-2xl"
        >
          <h1 className="text-center text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
            Sign Up
          </h1>

          {/* Username Input */}
          <div className="flex flex-col gap-2">
            <label htmlFor="username" className="font-semibold text-lg text-cyan-100">
              Username
            </label>
            <input
              type="text"
              name="username"
              id="username"
              placeholder="Enter your username..."
              className="bg-gray-700 border border-gray-600 p-3 rounded-lg text-white placeholder-gray-400 focus:border-cyan-500 focus:outline-none transition-colors"
              onChange={handleUserInput}
              value={signupData.username}
            />
          </div>

          {/* Email Input */}
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
              value={signupData.email}
            />
          </div>

          {/* Password Input */}
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
              value={signupData.password}
            />
          </div>

          <button
            type="submit"
            className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white py-3 rounded-lg font-bold text-lg transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/25 mt-4"
          >
            Create Account
          </button>

          <p className="text-center text-cyan-200 text-lg">
            Already have an account?{' '}
            <Link to="/login" className="text-cyan-400 hover:text-cyan-300 hover:underline">
              Login
            </Link>
          </p>
        </form>
      </div>
    </HomeLayout>
  );
}

export default Signup;
