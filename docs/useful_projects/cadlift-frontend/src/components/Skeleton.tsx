
import React from 'react';

interface SkeletonProps {
  className?: string;
}

const Skeleton: React.FC<SkeletonProps> = ({ className }) => {
  return (
    <div 
      className={`animate-pulse bg-slate-200 dark:bg-slate-800 rounded ${className}`}
    />
  );
};

export default Skeleton;
