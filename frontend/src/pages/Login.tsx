// src/pages/Login.tsx
import React from 'react';

const Login: React.FC = () => {
  return (
    <div className="max-w-md mx-auto mt-10 p-6 border rounded shadow">
      <h2 className="text-2xl font-bold mb-4 text-primary-800">Login</h2>
      <form className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-primary-700">Email</label>
          <input type="email" className="mt-1 block w-full border rounded p-2" placeholder="you@example.com" />
        </div>
        <div>
          <label className="block text-sm font-medium text-primary-700">Password</label>
          <input type="password" className="mt-1 block w-full border rounded p-2" placeholder="********" />
        </div>
        <button type="submit" className="w-full bg-primary-600 text-white py-2 rounded hover:bg-primary-700 transition">
          Sign In
        </button>
      </form>
    </div>
  );
};

export default Login;
