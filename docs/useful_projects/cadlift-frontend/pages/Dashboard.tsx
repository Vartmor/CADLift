import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UploadForm from '../components/UploadForm';
import JobStatusComponent from '../components/JobStatus';
import { UploadFormData } from '../types';
import { Terminal, LayoutDashboard, PenTool, LogOut } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleJobSubmit = async (data: UploadFormData) => {
    console.log("Submitting job:", data);
    // Mock latency simulation
    await new Promise(resolve => setTimeout(resolve, 800));
    const mockId = 'job_' + Math.random().toString(36).substr(2, 9);
    setCurrentJobId(mockId);
  };

  const resetJob = () => {
    setCurrentJobId(null);
  };

  const handleLogout = () => {
    navigate('/signin');
  };

  return (
    <div className="w-full max-w-7xl mx-auto animate-fade-in">
      {/* Dashboard Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
            <LayoutDashboard className="text-primary-500" />
            Workspace
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2 text-sm font-mono">
            <Terminal size={14} />
            <span>System ready. Waiting for input...</span>
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {!currentJobId && (
            <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-lg font-mono">
              <PenTool size={14} />
              <span>Mode: Standard Extrusion</span>
            </div>
          )}
          
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm font-bold text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-1.5 rounded-lg transition-colors"
          >
            <LogOut size={16} />
            <span className="hidden sm:inline">Log Out</span>
          </button>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="min-h-[600px]">
        {!currentJobId ? (
          <div className="w-full animate-fade-in-up">
             <UploadForm onSubmit={handleJobSubmit} />
          </div>
        ) : (
          <div className="w-full">
            <JobStatusComponent jobId={currentJobId} onReset={resetJob} />
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;