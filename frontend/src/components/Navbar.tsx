import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  const toggleDarkMode = () => {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  };

  // Load persisted theme on mount
  React.useEffect(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') document.documentElement.classList.add('dark');
  }, []);

  return (
    <nav className="bg-white/70 dark:bg-gray-900/70 backdrop-blur-md shadow-glass border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto flex justify-between items-center p-4">
        <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
          <Link to="/" className="hover:underline">MediMind AI</Link>
        </div>
        <ul className="flex space-x-4 items-center">
          <li><Link to="/" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Home</Link></li>
          <li><Link to="/dashboard" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Dashboard</Link></li>
          <li><Link to="/chat" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Chat</Link></li>
          <li><Link to="/knowledge" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Knowledge Base</Link></li>
          <li><Link to="/reports" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Reports</Link></li>
          <li><Link to="/profile" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Profile</Link></li>
          <li><Link to="/login" className="text-gray-800 dark:text-gray-200 hover:text-primary-600">Login</Link></li>
          <li>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-full bg-primary-100 dark:bg-primary-800 hover:bg-primary-200 dark:hover:bg-primary-700 transition"
              aria-label="Toggle dark mode"
            >
              {document.documentElement.classList.contains('dark') ? '☀️' : '🌙'}
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
