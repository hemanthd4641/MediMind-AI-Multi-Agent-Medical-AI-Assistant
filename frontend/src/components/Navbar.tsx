import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

const Navbar: React.FC = () => {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
      document.documentElement.classList.add('dark');
      setIsDark(true);
    }
  }, []);

  const toggleDarkMode = () => {
    document.documentElement.classList.toggle('dark');
    const isCurrentlyDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('theme', isCurrentlyDark ? 'dark' : 'light');
    setIsDark(isCurrentlyDark);
  };

  const handleLogout = async () => {
    try {
      if (token) {
         // Optionally notify backend if we used refresh tokens (not required here for simple clear)
      }
    } catch(e) {}
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white/70 dark:bg-gray-900/70 backdrop-blur-md shadow-glass border-b border-gray-200 dark:border-gray-700 relative z-50">
      <div className="container mx-auto flex justify-between items-center p-4">
        <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
          <Link to="/" className="hover:underline">MediMind AI</Link>
        </div>
        <ul className="flex space-x-4 items-center">
          {!user && (
            <li><Link to="/" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Home</Link></li>
          )}
          
          {user ? (
            <>
              <li><Link to="/dashboard" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Dashboard</Link></li>
              <li><Link to="/chat" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Chat</Link></li>
              <li><Link to="/knowledge" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Knowledge Base</Link></li>
              <li><Link to="/consultation" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Consultation</Link></li>
              <li><Link to="/reports" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Reports</Link></li>
              <li><Link to="/medications" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Medications</Link></li>

              <li><Link to="/profile" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Profile</Link></li>
              <li>
                <button onClick={handleLogout} className="text-red-500 hover:text-red-700">Logout</button>
              </li>
            </>
          ) : (
            <li><Link to="/login" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Login</Link></li>
          )}

          <li>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-full bg-primary-100 dark:bg-primary-800 hover:bg-primary-200 dark:hover:bg-primary-700 transition"
              aria-label="Toggle dark mode"
            >
              {isDark ? '☀️' : '🌙'}
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
