import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { careerAPI } from '../../api';
import Button from '../ui/Button.jsx';
import ProgressBar from '../ui/ProgressBar.jsx';

const AIRecommendations = () => {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['career', 'ai_recommendations'],
    queryFn: async () => {
      try {
        const res = await careerAPI.getSkillRecommendations();
        return res;
      } catch (err) {
        console.error('Failed to fetch AI recommendations', err);
        return [];
      }
    },
    staleTime: 5 * 60 * 1000,
  });

  const createSkill = useMutation({
    mutationFn: async (skill) => {
      return careerAPI.createSkill(skill);
    },
    onSuccess: (created) => {
      // Update caches
      queryClient.invalidateQueries(['career', 'skills']);
      queryClient.invalidateQueries(['career', 'dashboard']);
    },
    onError: (err) => {
      console.error('Failed to create skill from recommendation', err);
    }
  });

  if (isLoading) return <div className="text-sm text-gray-500">Loading recommendations...</div>;
  if (error) return <div className="text-sm text-red-500">Failed to load recommendations</div>;

  const recommendations = Array.isArray(data) ? data : (data && data.recommendations) ? data.recommendations : [];

  if (!recommendations || recommendations.length === 0) {
    return <div className="text-sm text-gray-500">No AI recommendations at the moment.</div>;
  }

  return (
    <div className="space-y-3">
      {recommendations.map((rec, idx) => (
        <div key={rec.id || idx} className="p-3 bg-gray-50 rounded-lg border">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-medium text-gray-900">{rec.name || rec.skill || 'Suggested Skill'}</h4>
              {rec.reason && <p className="text-sm text-gray-500 mt-1">{rec.reason}</p>}
              {rec.confidence && <p className="text-xs text-gray-400 mt-1">Confidence: {(rec.confidence * 100).toFixed(0)}%</p>}
            </div>
            <div className="flex flex-col items-end space-y-2">
              <Button size="sm" onClick={() => createSkill.mutate({ name: rec.name || rec.skill, current_level: rec.level || 1 })}>
                Add Skill
              </Button>
            </div>
          </div>
          {rec.suggested_progress && (
            <div className="mt-3">
              <ProgressBar progress={rec.suggested_progress} size="sm" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default AIRecommendations;
