// Lightweight mock data used by the frontend when the backend is unreachable
// Keep the shape similar to what the career dashboard endpoint returns

export const mockCareerData = {
  recent_goals: [
    {
      id: `mock-${Date.now() - 1000 * 60 * 60}`,
      title: 'Improve frontend skills',
      description: 'Work through component patterns and hooks',
      status: 'in_progress',
      priority: 'medium',
      progress: 25,
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: `mock-${Date.now() - 1000 * 60 * 60 * 24 * 7}`,
      title: 'Learn SQLAlchemy migrations',
      description: 'Understand Alembic operations and safe migrations',
      status: 'todo',
      priority: 'high',
      progress: 0,
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7).toISOString(),
      updated_at: new Date().toISOString(),
    }
  ],
  stats: {
    total_goals: 2,
    completed_goals: 0,
    in_progress: 1,
  },
  skills: [
    { id: 'mock-skill-1', name: 'React', level: 'intermediate', category: 'frontend' },
    { id: 'mock-skill-2', name: 'SQLAlchemy', level: 'beginner', category: 'backend' }
  ]
};

export default mockCareerData;
