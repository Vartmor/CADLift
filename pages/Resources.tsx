import React from 'react';
import { useTranslation } from 'react-i18next';

const cards = (t: any) => [
  { key: 'docs', title: t('resourcesPage.cards.docs.title'), desc: t('resourcesPage.cards.docs.desc'), href: 'http://localhost:8000/docs' },
  { key: 'videos', title: t('resourcesPage.cards.videos.title'), desc: t('resourcesPage.cards.videos.desc'), href: '#' },
  { key: 'faq', title: t('resourcesPage.cards.faq.title'), desc: t('resourcesPage.cards.faq.desc'), href: '#' },
  { key: 'community', title: t('resourcesPage.cards.community.title'), desc: t('resourcesPage.cards.community.desc'), href: '#' },
];

const Resources: React.FC = () => {
  const { t } = useTranslation();
  const items = cards(t);

  return (
    <div className="container mx-auto px-4 py-12 md:py-16 lg:py-20">
      <div className="max-w-3xl mx-auto text-center mb-12">
        <p className="text-xs font-bold uppercase tracking-[0.3em] text-primary-500 mb-3">Resources</p>
        <h1 className="text-4xl md:text-5xl font-black text-slate-900 dark:text-white mb-4">
          {t('resourcesPage.heading')}
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-300">
          {t('resourcesPage.subheading')}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8 max-w-5xl mx-auto">
        {items.map((item) => (
          <a
            key={item.key}
            href={item.href}
            target={item.href?.startsWith('http') ? '_blank' : undefined}
            rel="noreferrer"
            className="group rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/70 shadow-sm hover:shadow-xl transition-all duration-200 p-6 flex flex-col gap-3"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">{item.title}</h3>
              <span className="text-primary-500 text-sm font-semibold group-hover:translate-x-1 transition-transform">
                →
              </span>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{item.desc}</p>
          </a>
        ))}
      </div>
    </div>
  );
};

export default Resources;
