import React from 'react';

export interface StatItem {
    label: string;
    value: string;
}

interface HeroStatsProps {
    stats: StatItem[];
}

const HeroStats: React.FC<HeroStatsProps> = ({ stats }) => {
    return (
        <div className="flex flex-wrap gap-3 justify-start md:justify-end">
            {stats.map((stat) => (
                <div
                    key={stat.label}
                    className="min-w-[140px] rounded-2xl bg-white/90 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 shadow-sm p-4 hover:shadow-md transition-shadow"
                >
                    <p className="text-3xl font-black text-slate-900 dark:text-white">{stat.value}</p>
                    <p className="text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">
                        {stat.label}
                    </p>
                </div>
            ))}
        </div>
    );
};

export default HeroStats;
