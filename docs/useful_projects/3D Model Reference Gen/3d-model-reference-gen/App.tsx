import React, { useState, useEffect } from 'react';
import { Generator } from './components/Generator';
import { CubeIcon } from './components/Icons';

// Use a local interface casting to avoid global namespace conflicts with existing AIStudio definitions
interface AIStudioWindow extends Window {
  aistudio?: {
    hasSelectedApiKey: () => Promise<boolean>;
    openSelectKey: () => Promise<void>;
  };
}

function App() {
  const [hasKey, setHasKey] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkKey = async () => {
      try {
        const win = window as unknown as AIStudioWindow;
        if (win.aistudio && win.aistudio.hasSelectedApiKey) {
          const selected = await win.aistudio.hasSelectedApiKey();
          setHasKey(selected);
        } else if (process.env.API_KEY) {
          // Fallback if not running in the specific environment that supports aistudio object,
          // but strictly speaking, Veo/Pro Image requires the selector.
          setHasKey(true);
        }
      } catch (e) {
        console.error("Error checking API key:", e);
      } finally {
        setChecking(false);
      }
    };
    checkKey();
  }, []);

  const handleSelectKey = async () => {
    const win = window as unknown as AIStudioWindow;
    if (win.aistudio && win.aistudio.openSelectKey) {
      try {
        await win.aistudio.openSelectKey();
        // Assuming success after returning from openSelectKey, as per instructions to handle race condition
        setHasKey(true);
      } catch (error) {
        console.error("Error selecting key:", error);
      }
    } else {
      console.warn("API Key selector not available");
    }
  };

  const handleAuthError = () => {
    console.log("Authentication failed, resetting key state.");
    setHasKey(false);
  };

  if (checking) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // API Key Selection Screen
  if (!hasKey) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-center text-slate-100 font-sans selection:bg-blue-500/30">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl max-w-md w-full shadow-2xl">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/20">
            <CubeIcon className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-3">Authentication Required</h2>
          <p className="text-slate-400 mb-8 leading-relaxed text-sm">
            To use the professional <b>Nano Banana Pro</b> (Gemini 3 Pro) 3D reference generator, you must connect a Google Cloud Project with billing enabled.
          </p>
          
          <button 
            onClick={handleSelectKey}
            className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-xl transition-all shadow-lg active:scale-95 mb-6 flex items-center justify-center gap-2"
          >
            Connect Google Cloud Project
          </button>

          <p className="text-xs text-slate-500">
            Learn more about billing at <a href="https://ai.google.dev/gemini-api/docs/billing" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">ai.google.dev/gemini-api/docs/billing</a>
          </p>
        </div>
      </div>
    );
  }

  // Main App
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-500/30">
      
      {/* Navbar / Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-2 rounded-lg shadow-lg shadow-blue-500/20">
              <CubeIcon className="w-6 h-6 text-white" />
            </div>
            <h1 className="font-bold text-xl tracking-tight text-white">
              Model<span className="text-blue-400">Gen</span> Studio
            </h1>
          </div>
          <div className="text-xs font-mono text-slate-500 hidden sm:block">
            v1.0.0 • POWERED BY GEMINI 3 PRO
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-200 via-white to-indigo-200 mb-4">
            Concept to Mesh. Instantly.
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto text-lg leading-relaxed">
            Generate professional 3D modeling reference sheets from simple text descriptions. 
            Optimized for structure, lighting, and clarity.
          </p>
        </div>

        <Generator onAuthError={handleAuthError} />

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 mt-auto py-8 text-center text-slate-600 text-sm">
        <p>&copy; {new Date().getFullYear()} ModelGen Studio. Using Google Gemini Nano Banana Pro.</p>
      </footer>
    </div>
  );
}

export default App;