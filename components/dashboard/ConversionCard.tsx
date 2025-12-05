import React from 'react';
import { ArrowRight } from 'lucide-react';

export interface ConversionCardData {
    id: string;
    title: string;
    description: string;
    tag: string;
    icon: React.ReactNode;
    gradient: string;
    cta: string;
    action: () => void;
    comingSoon: boolean;
    extra?: React.ReactNode;
}

interface ConversionCardProps {
    card: ConversionCardData;
    comingSoonLabel: string;
}

const getIconBgColor = (id: string): string => {
    switch (id) {
        case 'cad':
            return 'bg-primary-500';
        case 'image':
            return 'bg-purple-500';
        case 'prompt':
            return 'bg-amber-500';
        default:
            return 'bg-slate-500';
    }
};

const ConversionCard: React.FC<ConversionCardProps> = ({ card, comingSoonLabel }) => {
    return (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-gradient-to-br from-white/90 via-white to-white/90 dark:from-slate-900/80 dark:via-slate-900/70 dark:to-slate-900/80 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                    <div
                        className={`w-10 h-10 rounded-xl flex items-center justify-center text-white ${getIconBgColor(card.id)}`}
                    >
                        {card.icon}
                    </div>
                    <div>
                        <p className="text-[11px] uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">
                            {card.tag}
                        </p>
                        <h4 className="text-base font-bold text-slate-900 dark:text-white">{card.title}</h4>
                        <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-3">
                            {card.description}
                        </p>
                    </div>
                </div>
                <button
                    type="button"
                    onClick={card.comingSoon ? undefined : card.action}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:-translate-y-0.5 transition-transform disabled:opacity-60 disabled:hover:translate-y-0"
                    disabled={card.comingSoon}
                >
                    {card.comingSoon ? comingSoonLabel : card.cta}
                    {!card.comingSoon && <ArrowRight size={14} />}
                </button>
            </div>
            {card.extra && <div className="mt-3">{card.extra}</div>}
        </div>
    );
};

export default ConversionCard;
