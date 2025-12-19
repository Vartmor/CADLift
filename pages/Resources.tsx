import React from 'react';
import { useTranslation } from 'react-i18next';
import { BookOpen, PlayCircle, HelpCircle, Users, ArrowUpRight, Terminal, Zap, Layers } from 'lucide-react';
import { env } from '../config/env';

const Resources: React.FC = () => {
  const { t } = useTranslation();

  const resources = [
    {
      key: 'docs',
      title: t('resourcesPage.cards.docs.title'),
      desc: t('resourcesPage.cards.docs.desc'),
      href: `${env.API_BASE_URL}/docs`,
      icon: Terminal,
      accent: 'from-cyan-500 to-blue-600',
      number: '01',
    },
    {
      key: 'videos',
      title: t('resourcesPage.cards.videos.title'),
      desc: t('resourcesPage.cards.videos.desc'),
      href: '#',
      icon: PlayCircle,
      accent: 'from-violet-500 to-purple-600',
      number: '02',
    },
    {
      key: 'faq',
      title: t('resourcesPage.cards.faq.title'),
      desc: t('resourcesPage.cards.faq.desc'),
      href: '#',
      icon: HelpCircle,
      accent: 'from-amber-500 to-orange-600',
      number: '03',
    },
    {
      key: 'community',
      title: t('resourcesPage.cards.community.title'),
      desc: t('resourcesPage.cards.community.desc'),
      href: '#',
      icon: Users,
      accent: 'from-emerald-500 to-teal-600',
      number: '04',
    },
  ];

  return (
    <div className="min-h-[80vh] relative">
      {/* Geometric background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-64 h-64 border border-slate-200 dark:border-slate-800 rotate-45 opacity-50" />
        <div className="absolute top-40 left-20 w-32 h-32 border border-slate-200 dark:border-slate-800 rotate-45 opacity-30" />
        <div className="absolute bottom-20 right-10 w-80 h-80 border border-slate-200 dark:border-slate-800 rotate-12 opacity-40" />
        <div className="absolute top-1/3 right-1/4 w-2 h-2 bg-primary-500 rotate-45" />
        <div className="absolute top-1/2 left-1/3 w-3 h-3 bg-violet-500 rotate-45" />
        <div className="absolute bottom-1/3 right-1/3 w-2 h-2 bg-amber-500 rotate-45" />
      </div>

      <div className="container mx-auto px-4 py-16 md:py-24 relative z-10">
        {/* Header Section - Brutalist Typography */}
        <div className="max-w-4xl mx-auto mb-20">
          <div className="flex items-center gap-4 mb-6">
            <div className="h-px flex-1 bg-slate-300 dark:bg-slate-700" />
            <span className="text-xs font-mono uppercase tracking-[0.5em] text-slate-500 dark:text-slate-400">
              Resources
            </span>
            <div className="h-px flex-1 bg-slate-300 dark:bg-slate-700" />
          </div>

          <h1 className="text-5xl md:text-7xl font-black text-slate-900 dark:text-white leading-[0.9] tracking-tight">
            {t('resourcesPage.heading')}
          </h1>

          <div className="mt-8 flex items-start gap-6">
            <div className="w-16 h-16 flex-shrink-0 border-2 border-slate-900 dark:border-white flex items-center justify-center">
              <Layers size={28} className="text-slate-900 dark:text-white" />
            </div>
            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-300 leading-relaxed max-w-xl">
              {t('resourcesPage.subheading')}
            </p>
          </div>
        </div>

        {/* Resources Grid - Asymmetric Layout */}
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {resources.map((item, index) => {
              const Icon = item.icon;
              // Asymmetric grid spans
              const spans = ['lg:col-span-7', 'lg:col-span-5', 'lg:col-span-5', 'lg:col-span-7'];

              return (
                <a
                  key={item.key}
                  href={item.href}
                  target={item.href?.startsWith('http') ? '_blank' : undefined}
                  rel="noreferrer"
                  className={`group relative ${spans[index]} bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 overflow-hidden transition-all duration-300 hover:border-slate-400 dark:hover:border-slate-600`}
                >
                  {/* Number watermark */}
                  <div className="absolute top-4 right-4 text-[120px] font-black leading-none text-slate-100 dark:text-slate-800/50 select-none pointer-events-none">
                    {item.number}
                  </div>

                  {/* Content */}
                  <div className="relative p-8 md:p-10 min-h-[280px] flex flex-col justify-between">
                    {/* Top row */}
                    <div className="flex items-start justify-between mb-8">
                      <div className={`w-14 h-14 flex items-center justify-center bg-gradient-to-br ${item.accent}`}>
                        <Icon size={28} className="text-white" />
                      </div>
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <ArrowUpRight size={24} className="text-slate-400" />
                      </div>
                    </div>

                    {/* Bottom content */}
                    <div>
                      <h3 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-3 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                        {item.title}
                      </h3>
                      <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                        {item.desc}
                      </p>
                    </div>

                    {/* Hover accent line */}
                    <div className={`absolute bottom-0 left-0 h-1 w-0 group-hover:w-full transition-all duration-500 bg-gradient-to-r ${item.accent}`} />
                  </div>
                </a>
              );
            })}
          </div>
        </div>

        {/* Bottom Section - Quick Links */}
        <div className="max-w-6xl mx-auto mt-20">
          <div className="border-t border-slate-200 dark:border-slate-800 pt-12">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div className="flex items-center gap-4">
                <Zap size={20} className="text-primary-500" />
                <span className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  Need quick help? Check our API documentation for instant integration.
                </span>
              </div>
              <a
                href={`${env.API_BASE_URL}/docs`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-semibold text-sm hover:bg-slate-800 dark:hover:bg-slate-100 transition-colors"
              >
                Open API Docs
                <ArrowUpRight size={16} />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Resources;
