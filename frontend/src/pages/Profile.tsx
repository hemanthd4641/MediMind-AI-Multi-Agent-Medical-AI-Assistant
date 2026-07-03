// src/pages/Profile.tsx
import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { UserCircle, Mail, Hash, Tag } from 'lucide-react';

const Profile: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="p-6">
        <p className="text-gray-500 dark:text-gray-400">Loading user profile...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto mt-8 p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700">
      <div className="flex items-center space-x-4 mb-8 pb-6 border-b border-gray-200 dark:border-gray-700">
        <div className="bg-primary-100 dark:bg-primary-900/30 p-4 rounded-full">
          <UserCircle className="h-16 w-16 text-primary-600 dark:text-primary-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{user.full_name}</h1>
          <p className="text-primary-600 dark:text-primary-400 font-medium capitalize">{user.role.replace('_', ' ')}</p>
        </div>
      </div>

      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Account Information</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
            <Mail className="h-6 w-6 text-gray-400 mt-1" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Email Address</p>
              <p className="font-medium text-gray-900 dark:text-gray-100">{user.email}</p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
            <Hash className="h-6 w-6 text-gray-400 mt-1" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">User ID</p>
              <p className="font-mono text-sm text-gray-900 dark:text-gray-100 mt-1">{user.id}</p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
            <Tag className="h-6 w-6 text-gray-400 mt-1" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Account Role</p>
              <p className="font-medium text-gray-900 dark:text-gray-100 capitalize">{user.role.replace('_', ' ')}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
