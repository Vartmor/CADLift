import { useEffect, useState } from 'react';
import { JobRecord, jobService } from '../services/jobService';

export const useJobPolling = (jobId: string | null, intervalMs = 1500) => {
  const [job, setJob] = useState<JobRecord | null>(null);

  useEffect(() => {
    if (!jobId) {
      setJob(null);
      return;
    }

    let cancelled = false;

    const fetchJob = async () => {
      const latest = await jobService.getJob(jobId);
      if (!cancelled) {
        setJob(latest);
      }
    };

    fetchJob();
    const timer = setInterval(fetchJob, intervalMs);
    const unsubscribe = jobService.subscribe((changedId) => {
      if (changedId && changedId !== jobId) return;
      fetchJob();
    });

    return () => {
      cancelled = true;
      clearInterval(timer);
      unsubscribe();
    };
  }, [jobId, intervalMs]);

  return job;
};
