import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Chat from './pages/Chat';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { ClinicalInterview } from './pages/ClinicalInterview';
import { ConsultationSummary } from './pages/ConsultationSummary';
import { MedicalReports } from './pages/MedicalReports';
import { ReportDetails } from './pages/ReportDetails';
import { MedicationCenter } from './pages/MedicationCenter';
import { PrescriptionDetails } from './pages/PrescriptionDetails';
import { MedicationTimeline } from './components/MedicationTimeline';
import { PatientDashboard } from './pages/PatientDashboard';
import { HealthTimeline } from './pages/HealthTimeline';
import { HealthTrends } from './pages/HealthTrends';

import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow container mx-auto p-4">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/profile" element={<Profile />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/dashboard" element={<PatientDashboard />} />
              <Route path="/timeline" element={<HealthTimeline />} />
              <Route path="/trends" element={<HealthTrends />} />
              <Route path="/knowledge" element={<KnowledgeBase />} />
              <Route path="/consultation" element={<ClinicalInterview />} />
              <Route path="/consultation/:id/summary" element={<ConsultationSummary />} />
              <Route path="/reports" element={<MedicalReports />} />
              <Route path="/reports/:id" element={<ReportDetails />} />
              <Route path="/medications" element={<MedicationCenter />} />
              <Route path="/medications/prescription/:id" element={<PrescriptionDetails />} />
              <Route path="/medications/timeline" element={<MedicationTimeline />} />
              <Route path="/settings" element={<Settings />} />

            </Route>

            {/* Catch All */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <footer className="bg-primary-800 text-white text-center py-4">
          © {new Date().getFullYear()} MediMind AI. All rights reserved.
        </footer>
      </div>
    </AuthProvider>
  );
};

export default App;
