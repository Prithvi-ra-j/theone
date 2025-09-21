import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { careerAPI } from '../api';
import Button from './ui/Button';
import ProgressBar from './ui/ProgressBar';

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
              <h4 className="font-medium text-gray-900">{rec.skill_name || rec.name || rec.skill || 'Suggested Skill'}</h4>
              {rec.reason && <p className="text-sm text-gray-500 mt-1">{rec.reason}</p>}
              {rec.description && <p className="text-sm text-gray-600 mt-1">{rec.description}</p>}
              {rec.priority && <p className="text-xs text-gray-400 mt-1">Priority: {rec.priority}</p>}
            </div>
            <div className="flex flex-col items-end space-y-2">
              <Button size="sm" onClick={() => createSkill.mutate({ 
                name: rec.skill_name || rec.name || rec.skill, 
                description: rec.description || '',
                current_level: rec.level || 1 
              })}>
                Add Skill
              </Button>
            </div>
          </div>
          {rec.related_skills && rec.related_skills.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-500">Related skills:</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {rec.related_skills.map((skill, i) => (
                  <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default AIRecommendations;