import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { opportunitiesAPI } from '../api';
import { ExternalLink, MapPin, Briefcase, Clock, Globe } from 'lucide-react';

const OpportunitiesFeed = ({ query = '', remoteOnly = false, limit = 8 }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['opportunities', { query, remoteOnly, limit }],
    queryFn: async () => {
      const res = await opportunitiesAPI.getOpportunities({ q: query, remote: remoteOnly, limit });
      return Array.isArray(res) ? res : (res?.items || res?.opportunities || []);
    },
    staleTime: 60_000,
  });

  if (isLoading) return <div className="text-sm text-gray-500">Loading opportunities…</div>;
  if (error) return <div className="text-sm text-red-500">Failed to load opportunities</div>;

  const items = data || [];
  if (!items.length) return <div className="text-sm text-gray-500">No opportunities found right now.</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {items.map((op, idx) => (
        <a
          key={op.id || idx}
          href={op.url || op.link || '#'}
          target="_blank"
          rel="noreferrer"
          className="block p-4 rounded-lg border bg-white dark:bg-gray-800 dark:border-gray-700 hover:shadow transition"
        >
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-gray-100">{op.title || 'Opportunity'}</h4>
              {op.company && (
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-0.5 flex items-center gap-1">
                  <Briefcase className="w-4 h-4" /> {op.company}
                </p>
              )}
              <div className="flex flex-wrap gap-3 text-xs text-gray-600 dark:text-gray-300 mt-2">
                {op.location && (
                  <span className="inline-flex items-center gap-1"><MapPin className="w-3 h-3" /> {op.location}</span>
                )}
                {typeof op.remote === 'boolean' && (
                  <span className="inline-flex items-center gap-1"><Globe className="w-3 h-3" /> {op.remote ? 'Remote' : 'Onsite'}</span>
                )}
                {op.type && (
                  <span className="inline-flex items-center gap-1"><Clock className="w-3 h-3" /> {op.type}</span>
                )}
              </div>
              {op.description && (
                <p className="text-sm text-gray-700 dark:text-gray-200 mt-2 line-clamp-3">{op.description}</p>
              )}
              {Array.isArray(op.tags) && op.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {op.tags.slice(0, 6).map((t, i) => (
                    <span key={i} className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded">{t}</span>
                  ))}
                </div>
              )}
            </div>
            <ExternalLink className="w-4 h-4 text-gray-500" />
          </div>
        </a>
      ))}
    </div>
  );
};

export default OpportunitiesFeed;
