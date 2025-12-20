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
      title: t('about.workflows.dwg.title'),
      description: t('about.workflows.dwg.description'),
      color: 'purple'
    },
    {
      icon: <Image className="w-8 h-8" />,
      title: t('about.workflows.image.title'),
      description: t('about.workflows.image.description'),
      color: 'blue'
    },
    {
      icon: <MessageSquare className="w-8 h-8" />,
      title: t('about.workflows.prompt.title'),
      description: t('about.workflows.prompt.description'),
      color: 'orange'
    },
  ];

  const features = [
    { icon: <Eye size={20} />, text: t('about.features.viewer'), color: 'green' },
    { icon: <Download size={20} />, text: t('about.features.export'), color: 'pink' },
    { icon: <Zap size={20} />, text: t('about.features.realtime'), color: 'yellow' },
    { icon: <Shield size={20} />, text: t('about.features.local'), color: 'slate' },
  ];

  const techStack = [
    { name: t('about.tech.frontend'), items: ['React', 'TypeScript', 'Tailwind CSS', 'Vite'] },
    { name: t('about.tech.backend'), items: ['FastAPI', 'Python', 'SQLAlchemy', 'Celery'] },
    { name: t('about.tech.ai'), items: ['Stable Diffusion', 'TripoSR', 'OpenAI (optional)'] },
    { name: t('about.tech.cad'), items: ['ezdxf', 'co2tools', 'ODA Converter', 'trimesh'] },
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
          <span className="text-sm font-bold text-primary-700 dark:text-primary-300">{t('about.badge')}</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-black text-slate-900 dark:text-white mb-6 leading-tight tracking-tight">
          {t('about.hero.title1')} <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-purple-600">{t('about.hero.titleHighlight')}</span> {t('about.hero.title2')}
        </h1>

        <p className="text-xl text-slate-600 dark:text-slate-400 max-w-3xl mx-auto leading-relaxed">
          {t('about.hero.subtitle')}
        </p>
      </div>

      {/* 3 Workflows Section */}
      <div className="mb-20">
        <div className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-4">{t('about.workflows.title')}</h2>
          <p className="text-slate-500 dark:text-slate-400 max-w-2xl mx-auto">{t('about.workflows.subtitle')}</p>
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
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-4">{t('about.features.title')}</h2>
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
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-4">{t('about.tech.title')}</h2>
          <p className="text-slate-500 dark:text-slate-400">{t('about.tech.subtitle')}</p>
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
        <h2 className="text-3xl font-black text-white mb-4">{t('about.cta.title')}</h2>
        <p className="text-slate-300 mb-8 max-w-xl mx-auto">
          {t('about.cta.subtitle')}
        </p>
        <button
          onClick={() => window.open('https://github.com/Start-Up-Week/cadlift', '_blank')}
          className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-slate-900 bg-white rounded-xl hover:bg-slate-100 hover:scale-105 transition-all duration-200 shadow-xl"
        >
          {t('about.cta.button')}
          <ArrowRight className="ml-2 w-5 h-5" />
        </button>
      </div>

      {/* Footer Disclaimer */}
      <div className="mt-12 p-6 bg-slate-100 dark:bg-slate-900/50 rounded-2xl text-center border border-slate-200 dark:border-slate-800/50">
        <p className="text-slate-500 dark:text-slate-400 text-sm">
          {t('about.disclaimer')}
        </p>
      </div>
    </div>
  );
};

export default About;