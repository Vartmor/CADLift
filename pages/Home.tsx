import React, { useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  ArrowRight,
  Box,
  Layers,
  Ruler,
  Sparkles,
  MousePointer2,
  FileDigit,
  Cpu,
  Image,
  MessageSquare,
  Download,
  Eye,
  Zap,
  Play,
  ChevronDown,
  Wand2,
  Star,
  Check
} from 'lucide-react';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const howItWorksRef = useRef<HTMLDivElement>(null);
  const featuresRef = useRef<HTMLDivElement>(null);
  const { t } = useTranslation();

  // Scroll reveal effect
  useEffect(() => {
    const revealElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    revealElements.forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  const scrollToFeatures = () => {
    featuresRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="w-full flex flex-col relative overflow-hidden">

      {/* === HERO SECTION === */}
      <div className="min-h-screen relative flex items-center justify-center overflow-hidden">

        {/* Subtle Background Effects */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">

          {/* Subtle Morphing Blobs - Purple/Violet tones only */}
          <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-purple-500/10 dark:bg-purple-500/5 rounded-full blur-[150px] animate-morph" />
          <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-violet-400/10 dark:bg-violet-400/5 rounded-full blur-[130px] animate-morph animation-delay-2000" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-purple-600/8 dark:bg-purple-600/4 rounded-full blur-[100px] animate-scale-pulse" />

          {/* Subtle Grid Pattern */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.02)_1px,transparent_1px)] dark:bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:60px_60px]" />

          {/* Floating Particles */}
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="particle"
              style={{
                left: `${5 + i * 8}%`,
                animationDelay: `${i * 1.5}s`,
                animationDuration: `${15 + (i % 5) * 3}s`,
              }}
            />
          ))}

          {/* Rotating Orbit Rings - Subtle */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px]">
            <div className="absolute inset-0 border border-slate-300/20 dark:border-slate-600/10 rounded-full animate-[spin_80s_linear_infinite]" />
            <div className="absolute inset-12 border border-dashed border-purple-300/15 dark:border-purple-600/8 rounded-full animate-[spin_60s_linear_infinite_reverse]" />
            <div className="absolute inset-24 border border-slate-200/20 dark:border-slate-700/10 rounded-full animate-[spin_40s_linear_infinite]" />
            {/* Orbital dots */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-purple-400/60 rounded-full animate-pulse" />
            <div className="absolute bottom-12 right-12 w-2 h-2 bg-slate-400/40 rounded-full animate-pulse" />
          </div>

          {/* 3D Floating Cube */}
          <div className="absolute top-[20%] right-[15%] animate-float-slow hidden lg:block">
            <div className="w-20 h-20 relative" style={{ transformStyle: 'preserve-3d', animation: 'tilt 8s ease-in-out infinite' }}>
              <div className="absolute inset-0 border-2 border-primary-400/40 bg-primary-400/5 backdrop-blur-sm" style={{ transform: 'translateZ(40px)' }} />
              <div className="absolute inset-0 border-2 border-purple-400/40 bg-purple-400/5 backdrop-blur-sm" style={{ transform: 'rotateY(90deg) translateZ(40px)' }} />
              <div className="absolute inset-0 border-2 border-violet-400/40 bg-violet-400/5 backdrop-blur-sm" style={{ transform: 'rotateX(90deg) translateZ(40px)' }} />
            </div>
          </div>

          {/* Floating Geometric Shapes - Enhanced */}
          <div className="absolute top-[15%] left-[10%] animate-float-slow">
            <svg width="80" height="70" viewBox="0 0 80 70" className="text-purple-500/50 dark:text-purple-400/40 drop-shadow-lg">
              <polygon points="40,0 80,70 0,70" fill="none" stroke="currentColor" strokeWidth="2" />
              <polygon points="40,15 65,55 15,55" fill="currentColor" fillOpacity="0.1" stroke="currentColor" strokeWidth="1" />
            </svg>
          </div>

          <div className="absolute top-[25%] right-[20%] animate-float-slower hidden md:block">
            <svg width="60" height="52" viewBox="0 0 60 52" className="text-slate-400/40 dark:text-slate-500/30">
              <polygon points="30,0 60,15 60,37 30,52 0,37 0,15" fill="currentColor" fillOpacity="0.1" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>

          <div className="absolute bottom-[30%] left-[15%] animate-float-slow animation-delay-1000">
            <svg width="50" height="50" viewBox="0 0 50 50" className="text-primary-500/50 dark:text-primary-400/40">
              <rect x="5" y="5" width="40" height="40" fill="currentColor" fillOpacity="0.1" stroke="currentColor" strokeWidth="2" rx="4" transform="rotate(45 25 25)" />
            </svg>
          </div>

          <div className="absolute bottom-[25%] right-[12%] animate-float-slower animation-delay-2000">
            <svg width="55" height="55" viewBox="0 0 55 55" className="text-orange-500/50 dark:text-orange-400/40">
              <circle cx="27.5" cy="27.5" r="24" fill="currentColor" fillOpacity="0.05" stroke="currentColor" strokeWidth="2" />
              <circle cx="27.5" cy="27.5" r="12" fill="none" stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 4" />
            </svg>
          </div>

          <div className="absolute top-[35%] left-[5%] w-3 h-3 bg-purple-400/40 rounded-full blur-sm animate-pulse" />
          <div className="absolute top-[15%] right-[30%] w-2 h-2 bg-violet-400/40 rounded-full blur-sm animate-pulse animation-delay-1000" />
          <div className="absolute bottom-[45%] right-[8%] w-3 h-3 bg-slate-400/30 rounded-full blur-sm animate-pulse animation-delay-2000" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 text-center px-4 max-w-5xl mx-auto">

          {/* Animated Badge with Shimmer */}
          <div className="inline-flex items-center gap-2 px-6 py-3 mb-10 rounded-full glass-card shimmer border border-primary-200/50 dark:border-primary-700/30 shadow-2xl animate-fade-in-up glow-primary">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
            </span>
            <span className="text-sm font-bold bg-gradient-to-r from-primary-600 to-purple-600 dark:from-primary-400 dark:to-purple-400 bg-clip-text text-transparent">AI-Powered 3D Generation</span>
            <Sparkles size={16} className="text-primary-500 animate-pulse" />
          </div>

          {/* Main Headline with Gradient Animation */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tight text-slate-900 dark:text-white mb-8 leading-[0.95] animate-fade-in-up animation-delay-200">
            <span className="block mb-2">Turn</span>
            <span className="relative inline-block">
              <span className="gradient-text-animate font-black">
                Anything
              </span>
              <svg className="absolute -bottom-3 left-0 w-full" viewBox="0 0 200 12" fill="none">
                <path d="M2 10C50 2 150 2 198 10" stroke="url(#underline-gradient)" strokeWidth="4" strokeLinecap="round" className="animate-pulse" />
                <defs>
                  <linearGradient id="underline-gradient" x1="0" y1="0" x2="200" y2="0">
                    <stop stopColor="#06b6d4" />
                    <stop offset="0.5" stopColor="#8b5cf6" />
                    <stop offset="1" stopColor="#3b82f6" />
                  </linearGradient>
                </defs>
              </svg>
            </span>
            <br />
            <span className="text-slate-300 dark:text-slate-600">Into</span>{' '}
            <span className="relative">
              <span className="bg-gradient-to-r from-primary-500 via-purple-500 to-blue-500 bg-clip-text text-transparent glow-text">3D</span>
            </span>
          </h1>

          {/* Sub-headline */}
          <p className="text-xl md:text-2xl text-slate-600 dark:text-slate-400 mb-14 max-w-3xl mx-auto leading-relaxed animate-fade-in-up animation-delay-400">
            From <span className="font-bold text-purple-600 dark:text-purple-400">CAD files</span> to{' '}
            <span className="font-bold text-violet-600 dark:text-violet-400">images</span> to{' '}
            <span className="font-bold text-orange-600 dark:text-orange-400">text prompts</span> —{' '}
            generate production-ready 3D models in seconds.
          </p>

          {/* CTA Buttons with Glow */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-5 mb-16 animate-fade-in-up animation-delay-600">
            <button
              onClick={() => navigate('/dashboard')}
              className="group relative px-10 py-5 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 dark:from-white dark:via-slate-100 dark:to-white text-white dark:text-slate-900 rounded-2xl font-bold text-lg shadow-2xl hover:shadow-primary-500/20 dark:hover:shadow-primary-400/30 hover:scale-105 transition-all duration-300 flex items-center gap-3 overflow-hidden animate-glow"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 via-violet-600/20 to-pink-600/20 opacity-0 group-hover:opacity-100 transition-opacity" />
              <Play size={22} className="text-primary-400 dark:text-primary-600 relative z-10" />
              <span className="relative z-10">Start Creating</span>
              <ArrowRight size={22} className="group-hover:translate-x-1 transition-transform relative z-10" />
            </button>

            <button
              onClick={scrollToFeatures}
              className="group px-10 py-5 glass-card text-slate-700 dark:text-slate-200 rounded-2xl font-bold text-lg hover:border-primary-500 dark:hover:border-primary-400 shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center gap-2 hover-lift"
            >
              Explore Features
              <ChevronDown size={22} className="group-hover:translate-y-1 transition-transform" />
            </button>
          </div>

          {/* Input Types Preview - Glassmorphic Cards */}
          <div className="flex flex-wrap items-center justify-center gap-4 animate-fade-in-up animation-delay-1000">
            {[
              { icon: FileDigit, label: 'DWG / DXF', color: 'purple', gradient: 'from-purple-500 to-purple-700' },
              { icon: Image, label: 'Images', color: 'blue', gradient: 'from-blue-500 to-blue-700' },
              { icon: Wand2, label: 'AI Prompts', color: 'orange', gradient: 'from-orange-500 to-orange-700' },
            ].map((item, idx) => (
              <div
                key={idx}
                className="group flex items-center gap-3 px-6 py-4 rounded-2xl glass-card hover:scale-110 transition-all duration-300 cursor-pointer hover-lift"
                onClick={() => navigate('/dashboard')}
                style={{ animationDelay: `${1000 + idx * 150}ms` }}
              >
                <div className={`p-2.5 rounded-xl bg-gradient-to-br ${item.gradient} shadow-lg group-hover:scale-110 transition-transform`}>
                  <item.icon size={22} className="text-white" />
                </div>
                <span className="font-bold text-slate-700 dark:text-slate-200">{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Animated Scroll Indicator */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 opacity-60 animate-bounce">
          <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Scroll to explore</span>
          <ChevronDown size={24} className="text-primary-500" />
        </div>
      </div>

      {/* === FEATURES SECTION === */}
      <div ref={featuresRef} className="py-32 px-4 relative overflow-hidden">

        {/* Subtle Background */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-500/5 to-transparent dark:via-purple-500/3" />

        <div className="max-w-7xl mx-auto relative z-10">

          {/* Section Header */}
          <div className="text-center mb-20 reveal">
            <div className="inline-flex items-center gap-2 px-5 py-2.5 mb-8 rounded-full glass-card border border-primary-200/50 dark:border-primary-700/30 shadow-lg shimmer">
              <Zap size={18} className="text-primary-500" />
              <span className="text-sm font-bold bg-gradient-to-r from-primary-600 to-purple-600 dark:from-primary-400 dark:to-purple-400 bg-clip-text text-transparent">Powerful Features</span>
            </div>
            <h2 className="text-4xl md:text-6xl font-black text-slate-900 dark:text-white mb-6">
              Three Ways to{' '}
              <span className="gradient-text-animate">Create</span>
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
              Choose your input method. We handle the rest.
            </p>
          </div>

          {/* Feature Cards - Enhanced Bento Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* CAD Card - Large with Glassmorphism */}
            <div className="lg:row-span-2 group relative p-10 rounded-[2.5rem] bg-gradient-to-br from-purple-500 via-purple-600 to-purple-800 text-white overflow-hidden shadow-2xl shadow-purple-500/30 hover:shadow-purple-500/50 transition-all duration-500 hover:scale-[1.02] reveal-left tilt-card">
              {/* Glow effects */}
              <div className="absolute top-0 right-0 w-80 h-80 bg-white/20 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/2 animate-pulse" />
              <div className="absolute bottom-0 left-0 w-60 h-60 bg-black/20 rounded-full blur-[80px] translate-y-1/2 -translate-x-1/2" />

              {/* Floating decorative elements */}
              <div className="absolute top-10 right-10 w-20 h-20 border border-white/20 rounded-xl rotate-12 animate-float-slow" />
              <div className="absolute bottom-20 right-20 w-10 h-10 bg-white/10 rounded-lg rotate-45 animate-float-slower" />

              <div className="relative z-10">
                <div className="w-18 h-18 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center mb-8 shadow-xl group-hover:scale-110 transition-transform">
                  <FileDigit size={36} />
                </div>
                <h3 className="text-3xl font-black mb-5">DWG/DXF to 3D</h3>
                <p className="text-purple-100 text-lg leading-relaxed mb-10">
                  Upload AutoCAD files directly. We auto-detect layers, walls, and shapes — then extrude to 3D models.
                </p>
                <ul className="space-y-4 text-purple-100">
                  {['Native DWG support via ODA', 'All DXF versions', 'Auto layer detection', 'Closed shape extrusion'].map((item, i) => (
                    <li key={i} className="flex items-center gap-4 group/item">
                      <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center group-hover/item:bg-white/30 group-hover/item:scale-110 transition-all">
                        <Check size={14} />
                      </div>
                      <span className="font-medium">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Image Card */}
            <div className="group relative p-8 rounded-[2rem] bg-gradient-to-br from-indigo-500 via-indigo-600 to-violet-700 text-white overflow-hidden shadow-2xl shadow-indigo-500/30 hover:shadow-indigo-500/50 transition-all duration-500 hover:scale-[1.03] reveal tilt-card">
              <div className="absolute top-0 right-0 w-48 h-48 bg-white/20 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 animate-pulse" />
              <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-violet-400/30 rounded-full blur-[60px]" />

              <div className="relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center mb-6 shadow-xl group-hover:scale-110 transition-transform">
                  <Image size={32} />
                </div>
                <h3 className="text-2xl font-black mb-4">Image to 3D</h3>
                <p className="text-indigo-100 leading-relaxed text-lg">
                  Upload any image — photos, sketches, renders. Our AI reconstructs it in 3D using TripoSR.
                </p>
              </div>
            </div>

            {/* Prompt Card */}
            <div className="group relative p-8 rounded-[2rem] bg-gradient-to-br from-orange-500 via-orange-600 to-red-600 text-white overflow-hidden shadow-2xl shadow-orange-500/30 hover:shadow-orange-500/50 transition-all duration-500 hover:scale-[1.03] reveal animation-delay-200 tilt-card">
              <div className="absolute top-0 right-0 w-48 h-48 bg-white/20 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 animate-pulse" />
              <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-yellow-400/30 rounded-full blur-[60px]" />

              <div className="relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center mb-6 shadow-xl group-hover:scale-110 group-hover:rotate-12 transition-all">
                  <MessageSquare size={32} />
                </div>
                <h3 className="text-2xl font-black mb-4">Prompt to 3D</h3>
                <p className="text-orange-100 leading-relaxed text-lg">
                  Just describe it. Stable Diffusion generates an image, then TripoSR builds your 3D model.
                </p>
              </div>
            </div>

            {/* Viewer Card - Glassmorphic */}
            <div className="group relative p-7 rounded-[2rem] glass-card overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.03] reveal-right hover-lift">
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="flex items-center gap-5 relative z-10">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:rotate-6 transition-all">
                  <Eye size={26} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-1">3D Viewer</h3>
                  <p className="text-slate-500 dark:text-slate-400">Preview before download</p>
                </div>
              </div>
            </div>

            {/* Export Card - Glassmorphic */}
            <div className="group relative p-7 rounded-[2rem] glass-card overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-500 hover:scale-[1.03] reveal-right animation-delay-200 hover-lift">
              <div className="absolute inset-0 bg-gradient-to-br from-pink-500/10 to-rose-500/10 opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="flex items-center gap-5 relative z-10">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center shadow-lg group-hover:scale-110 group-hover:-rotate-6 transition-all">
                  <Download size={26} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-1">Multi-Format</h3>
                  <p className="text-slate-500 dark:text-slate-400">GLB, STL, DXF, STEP</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* === HOW IT WORKS === */}
      <div ref={howItWorksRef} className="py-32 px-4 relative overflow-hidden">

        {/* Subtle grid background */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] dark:bg-[linear-gradient(rgba(6,182,212,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.02)_1px,transparent_1px)] bg-[size:50px_50px]" />

        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-20 reveal">
            <h2 className="text-4xl md:text-6xl font-black text-slate-900 dark:text-white mb-6">
              How It{' '}
              <span className="gradient-text-animate">Works</span>
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-400">
              Three simple steps to 3D
            </p>
          </div>

          {/* Steps with connecting line */}
          <div className="relative">
            {/* Clean gradient connection line - no shimmer */}
            <div className="hidden md:block absolute top-12 left-[16.67%] right-[16.67%] h-0.5 bg-gradient-to-r from-purple-500/50 via-violet-400/50 to-pink-500/50 rounded-full" />

            {/* Connection dots */}
            <div className="hidden md:block absolute top-12 left-[16.67%] -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-purple-500 shadow-lg shadow-purple-500/50" />
            <div className="hidden md:block absolute top-12 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-violet-500 shadow-lg shadow-violet-500/50" />
            <div className="hidden md:block absolute top-12 right-[16.67%] translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-pink-500 shadow-lg shadow-pink-500/50" />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { step: '1', title: 'Upload or Describe', desc: 'Drop your CAD file, image, or type a prompt', icon: FileDigit, gradient: 'from-purple-500 to-violet-500' },
                { step: '2', title: 'AI Processing', desc: 'Our engines detect geometry and generate 3D', icon: Cpu, gradient: 'from-violet-500 to-purple-600' },
                { step: '3', title: 'View & Download', desc: 'Preview in 3D viewer, export in any format', icon: Box, gradient: 'from-purple-600 to-pink-500' },
              ].map((item, idx) => (
                <div key={idx} className={`relative group reveal ${idx === 1 ? 'animation-delay-200' : idx === 2 ? 'animation-delay-400' : ''}`}>

                  {/* Card */}
                  <div className="relative glass-card rounded-3xl p-10 shadow-xl hover:shadow-2xl transition-all duration-500 group-hover:-translate-y-2 overflow-hidden">
                    {/* Gradient accent on hover */}
                    <div className={`absolute inset-0 bg-gradient-to-br ${item.gradient} opacity-0 group-hover:opacity-5 transition-opacity`} />

                    {/* Step number badge */}
                    <div className={`absolute top-6 right-6 w-10 h-10 rounded-xl bg-gradient-to-br ${item.gradient} flex items-center justify-center shadow-lg`}>
                      <span className="text-white font-bold text-lg">{item.step}</span>
                    </div>

                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${item.gradient} flex items-center justify-center mb-8 shadow-xl group-hover:scale-110 group-hover:rotate-6 transition-all relative z-10`}>
                      <item.icon size={30} className="text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-4 relative z-10">{item.title}</h3>
                    <p className="text-slate-500 dark:text-slate-400 text-lg relative z-10">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* === FINAL CTA === */}
      <div className="py-32 px-4 relative overflow-hidden">

        {/* Dark gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900" />

        {/* Subtle glow effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/20 rounded-full blur-[150px] animate-morph" />
          <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-violet-500/15 rounded-full blur-[120px] animate-pulse" />
          <div className="absolute bottom-0 left-0 w-[250px] h-[250px] bg-purple-600/15 rounded-full blur-[100px] animate-pulse animation-delay-2000" />
        </div>

        {/* Floating stars/particles */}
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white/60 rounded-full animate-pulse"
            style={{
              top: `${20 + i * 10}%`,
              left: `${10 + i * 12}%`,
              animationDelay: `${i * 0.3}s`,
            }}
          />
        ))}

        <div className="max-w-4xl mx-auto text-center relative z-10 reveal">

          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-5 py-2.5 mb-10 rounded-full glass backdrop-blur-xl border border-white/20 shadow-2xl shimmer">
            <Star size={16} className="text-yellow-400" />
            <span className="text-sm font-bold text-white/90">Start for free</span>
            <Sparkles size={16} className="text-primary-400" />
          </div>

          <h2 className="text-5xl md:text-7xl font-black text-white mb-8">
            Ready to{' '}
            <span className="gradient-text-animate">Create</span>?
          </h2>
          <p className="text-xl md:text-2xl text-slate-300 mb-14 max-w-2xl mx-auto leading-relaxed">
            Transform CAD files, images, or ideas into 3D models. No credit card required.
          </p>

          <button
            onClick={() => navigate('/dashboard')}
            className="group relative px-12 py-6 bg-white text-slate-900 rounded-2xl font-bold text-xl shadow-2xl hover:shadow-white/30 hover:scale-105 transition-all duration-300 flex items-center gap-4 mx-auto overflow-hidden"
          >
            {/* Shimmer effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary-200/50 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

            <Play size={26} className="text-primary-600 relative z-10" />
            <span className="relative z-10">Open Dashboard</span>
            <ArrowRight size={26} className="group-hover:translate-x-2 transition-transform relative z-10" />
          </button>
        </div>
      </div>

      {/* Footer Gradient Ribbon */}
      <div className="h-2 bg-gradient-to-r from-purple-500 via-violet-500 via-pink-500 to-purple-600 animate-gradient" style={{ backgroundSize: '300% 100%' }} />
    </div>
  );
};

export default Home;
