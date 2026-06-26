// src/pages/Home.tsx
import React from 'react';

const Home: React.FC = () => {
  return (
    <section className="text-center py-20 bg-primary-50">
      <h1 className="text-5xl font-bold text-primary-800 mb-4">Welcome to MediMind AI</h1>
      <p className="text-lg text-primary-700 mb-8">
        A modern, production‑ready medical assistant platform.
      </p>
      <a
        href="/dashboard"
        className="bg-primary-600 text-white px-6 py-3 rounded hover:bg-primary-700 transition"
      >
        Get Started
      </a>
    </section>
  );
};

export default Home;
