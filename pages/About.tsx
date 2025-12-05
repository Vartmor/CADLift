import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Layers,
  Zap,
  Box,
  Code2,
  ArrowRight,
  Cpu,
  FileDigit,
  Image,
  MessageSquare,
  Download,
  Eye,
  Sparkles,
  Shield
} from 'lucide-react';

const About: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const capabilities = [
    {
      icon: <FileDigit className="w-8 h-8" />,
      title: 'DWG/DXF to 3D',
      description: 'Upload AutoCAD files (DWG or DXF) and we extrude closed shapes into 3D models. Supports walls, doors, windows detection.',
      color: 'purple'
    },
    {
      icon: <Image className="w-8 h-8" />,
      title: 'Image to 3D',
      description: 'Transform any 2D image into a detailed 3D model using TripoSR AI. Works with photos, sketches, and renders.',
      color: 'blue'
    },
    {
      icon: <MessageSquare className="w-8 h-8" />,
      title: 'Prompt to 3D',
      description: 'Describe your idea in text. Our AI generates an image with Stable Diffusion, then converts it to 3D.',
      color: 'orange'
    },
  ];

  const features = [
    { icon: <Eye size={20} />, text: 'Built-in 3D Viewer', color: 'green' },
    { icon: <Download size={20} />, text: 'GLB, STL, DXF, STEP Export', color: 'pink' },
    { icon: <Zap size={20} />, text: 'Real-Time Progress', color: 'yellow' },
    { icon: <Shield size={20} />, text: 'Local Processing', color: 'slate' },
  ];

  const techStack = [
    { name: 'Frontend', items: ['React', 'TypeScript', 'Tailwind CSS', 'Vite'] },
    { name: 'Backend', items: ['FastAPI', 'Python', 'SQLAlchemy', 'Celery'] },
    { name: 'AI Models', items: ['Stable Diffusion', 'TripoSR', 'OpenAI (optional)'] },
    { name: 'CAD Tools', items: ['ezdxf', 'co2tools', 'ODA Converter', 'trimesh'] },
  ];

  const colorClasses: Record<string, { bg: string; border: string; text: string }> = {
    purple: { bg: 'bg-purple-100 dark:bg-purple-900/30', border: 'border-purple-500', text: 'text-purple-600 dark:text-purple-400' },
    blue: { bg: 'bg-blue-100 dark:bg-blue-900/30', border: 'border-blue-500', text: 'text-blue-600 dark:text-blue-400' },
    orange: { bg: 'bg-orange-100 dark:bg-orange-900/30', border: 'border-orange-500', text: 'text-orange-600 dark:text-orange-400' },
    green: { bg: 'bg-green-100 dark:bg-green-900/30', border: 'border-green-500', text: 'text-green-600 dark:text-green-400' },
    pink: { bg: 'bg-pink-100 dark:bg-pink-900/30', border: 'border-pink-500', text: 'text-pink-600 dark:text-pink-400' },
    yellow: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', border: 'border-yellow-500', text: 'text-yellow-600 dark:text-yellow-400' },
    slate: { bg: 'bg-slate-100 dark:bg-slate-800', border: 'border-slate-500', text: 'text-slate-600 dark:text-slate-400' },
  };

  return (
    <div className="max-w-6xl mx-auto py-8 animate-fade-in">

      {/* Hero Section */}
      <div className="text-center mb-20">
        <div className="inline-flex items-center space-x-2 px-4 py-2 mb-8 rounded-full bg-primary-100 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-800">
          <Sparkles size={16} className="text-primary-600 dark:text-primary-400" />
          <span className="text-sm font-bold text-primary-700 dark:text-primary-300">AI-Powered 3D Generation</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-black text-slate-900 dark:text-white mb-6 leading-tight tracking-tight">
          Transform <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-purple-600">Anything</span> Into 3D
        </h1>

        <p className="text-xl text-slate-600 dark:text-slate-400 max-w-3xl mx-auto leading-relaxed">
          CADLift is an open-source platform that converts CAD files, images, and text prompts into production-ready 3D models using AI and advanced geometry processing.
        </p>
      </div>

      {/* 3 Workflows Section */}
      <div className="mb-20">
        <div className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-4">Three Ways to Create 3D</h2>
          <p className="text-slate-500 dark:text-slate-400 max-w-2xl mx-auto">Choose the workflow that fits your needs.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {capabilities.map((cap, idx) => {
            const colors = colorClasses[cap.color];
            return (
              <div
                key={idx}
                className={`p-8 rounded-3xl border-2 ${colors.border} bg-white dark:bg-slate-900 hover:scale-105 transition-all duration-300 shadow-lg`}
              >
                <div className={`w-16 h-16 rounded-2xl ${colors.bg} flex items-center justify-center mb-6`}>
                  <span className={colors.text}>{cap.icon}</span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{cap.title}</h3>
                <p className="text-slate-500 dark:text-slate-400 leading-relaxed">{cap.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Additional Features */}
      <div className="mb-20">
        <div className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-4">Plus These Features</h2>
        </div>

        <div className="flex flex-wrap justify-center gap-4">
          {features.map((feat, idx) => {
            const colors = colorClasses[feat.color];
            return (
              <div key={idx} className={`flex items-center space-x-3 ${colors.bg} px-5 py-3 rounded-full border ${colors.border}`}>
                <span className={colors.text}>{feat.icon}</span>
                <span className="font-semibold text-slate-700 dark:text-slate-200">{feat.text}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tech Stack */}
      <div className="mb-20">
        <div className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-4">Built With</h2>
          <p className="text-slate-500 dark:text-slate-400">Modern, open-source technologies.</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {techStack.map((stack, idx) => (
            <div key={idx} className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <h4 className="font-bold text-slate-900 dark:text-white mb-4 text-sm uppercase tracking-wider">{stack.name}</h4>
              <ul className="space-y-2">
                {stack.items.map((item, i) => (
                  <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 dark:from-slate-950 dark:to-slate-900 rounded-3xl p-12 text-center">
        <h2 className="text-3xl font-black text-white mb-4">Ready to Try?</h2>
        <p className="text-slate-300 mb-8 max-w-xl mx-auto">
          Start generating 3D models from CAD files, images, or text prompts right now.
        </p>
        <button
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-slate-900 bg-white rounded-xl hover:bg-slate-100 hover:scale-105 transition-all duration-200 shadow-xl"
        >
          Open Dashboard
          <ArrowRight className="ml-2 w-5 h-5" />
        </button>
      </div>

      {/* Footer Disclaimer */}
      <div className="mt-12 p-6 bg-slate-100 dark:bg-slate-900/50 rounded-2xl text-center border border-slate-200 dark:border-slate-800/50">
        <p className="text-slate-500 dark:text-slate-400 text-sm">
          CADLift is an open-source project. AI features require model downloads on first use.
        </p>
      </div>
    </div>
  );
};

export default About;