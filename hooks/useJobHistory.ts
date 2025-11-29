import { useEffect, useState } from 'react';
import { JobRecord, jobService } from '../services/jobService';

export const useJobHistory = (intervalMs = 4000) => {
  const [jobs, setJobs] = useState<JobRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchJobs = async () => {
      const list = await jobService.listJobs();
      if (!cancelled) {
        setJobs(list);
        setIsLoading(false);
      }
    };

    fetchJobs();
    const timer = setInterval(fetchJobs, intervalMs);
    const unsubscribe = jobService.subscribe(fetchJobs);

    return () => {
      cancelled = true;
      clearInterval(timer);
      unsubscribe();
    };
  }, [intervalMs]);

  return { jobs, isLoading };
};
