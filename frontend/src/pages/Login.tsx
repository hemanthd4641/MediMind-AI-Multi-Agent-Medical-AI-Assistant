// src/pages/Login.tsx
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

const Login: React.FC = () => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      let res;
      if (isRegistering) {
        res = await api.post('/api/v1/auth/register', { 
          full_name: fullName,
          email, 
          password 
        });
      } else {
        res = await api.post('/api/v1/auth/login', { email, password });
      }
      
      // Fetch user profile using the returned token
      const userRes = await api.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${res.data.access_token}` }
      });
      
      login(res.data.access_token, userRes.data);
      navigate('/dashboard');
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Authentication failed. Please check your details.');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 border rounded shadow bg-white dark:bg-gray-800 dark:border-gray-700">
      <h2 className="text-2xl font-bold mb-4 text-primary-800 dark:text-primary-400">
        {isRegistering ? 'Create an Account' : 'Login'}
      </h2>
      
      {error && <div className="mb-4 text-red-500 text-sm bg-red-100 dark:bg-red-900/30 p-2 rounded">{error}</div>}
      
      <form className="space-y-4" onSubmit={handleSubmit}>
        {isRegistering && (
          <div>
            <label className="block text-sm font-medium text-primary-700 dark:text-gray-300">Full Name</label>
            <input 
              type="text" 
              className="mt-1 block w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
              placeholder="John Doe" 
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required={isRegistering}
            />
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-primary-700 dark:text-gray-300">Email</label>
          <input 
            type="email" 
            className="mt-1 block w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
            placeholder="you@example.com" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-primary-700 dark:text-gray-300">Password</label>
          <input 
            type="password" 
            className="mt-1 block w-full border rounded p-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
            placeholder="********" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </div>
        <button type="submit" className="w-full bg-primary-600 text-white py-2 rounded hover:bg-primary-700 transition">
          {isRegistering ? 'Sign Up' : 'Sign In'}
        </button>
      </form>
      
      <div className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
        {isRegistering ? (
          <p>
            Already have an account?{' '}
            <button onClick={() => setIsRegistering(false)} className="text-primary-600 dark:text-primary-400 hover:underline">
              Login here
            </button>
          </p>
        ) : (
          <p>
            Don't have an account?{' '}
            <button onClick={() => setIsRegistering(true)} className="text-primary-600 dark:text-primary-400 hover:underline">
              Sign up here
            </button>
          </p>
        )}
      </div>
    </div>
  );
};

export default Login;
