-- Initialize Dristhi database
-- This script sets up the initial database structure and sample data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create sample badges
INSERT INTO badge (name, description, icon_url, category, points, is_hidden, created_at) VALUES
('First Steps', 'Complete your first habit', '/icons/first-steps.svg', 'habits', 10, false, NOW()),
('Goal Setter', 'Create your first career goal', '/icons/goal-setter.svg', 'career', 20, false, NOW()),
('Consistent', 'Maintain a 7-day habit streak', '/icons/consistent.svg', 'habits', 50, false, NOW()),
('Financial Guru', 'Create your first budget', '/icons/financial-guru.svg', 'finance', 30, false, NOW()),
('Wellness Warrior', 'Log your mood for 5 days', '/icons/wellness-warrior.svg', 'mood', 25, false, NOW()),
('Skill Master', 'Reach level 5 in any skill', '/icons/skill-master.svg', 'career', 100, false, NOW()),
('Budget Hero', 'Stay within budget for a month', '/icons/budget-hero.svg', 'finance', 75, false, NOW()),
('Mood Tracker', 'Log mood for 30 consecutive days', '/icons/mood-tracker.svg', 'mood', 150, false, NOW()),
('Habit Champion', 'Maintain a 30-day habit streak', '/icons/habit-champion.svg', 'habits', 200, false, NOW()),
('Career Planner', 'Complete 5 career goals', '/icons/career-planner.svg', 'career', 300, false, NOW())
ON CONFLICT (name) DO NOTHING;

-- Create sample categories for expenses
-- Note: These would typically be created by the application, but we'll add some defaults
-- The actual expense categories will be managed by the application

-- Create sample financial categories
-- Note: In a real application, these would be configurable by the user
-- For now, we'll just ensure the database is ready

-- Set up any additional database configurations
-- This could include:
-- - Custom functions
-- - Triggers
-- - Views
-- - Additional indexes

-- Example: Create a function to calculate user progress
CREATE OR REPLACE FUNCTION calculate_user_progress(user_id_param INTEGER)
RETURNS TABLE(
    total_goals INTEGER,
    completed_goals INTEGER,
    total_habits INTEGER,
    active_habits INTEGER,
    total_xp INTEGER,
    level INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(COUNT(cg.id), 0) as total_goals,
        COALESCE(COUNT(CASE WHEN cg.status = 'completed' THEN 1 END), 0) as completed_goals,
        COALESCE(COUNT(h.id), 0) as total_habits,
        COALESCE(COUNT(CASE WHEN h.is_active = true THEN 1 END), 0) as active_habits,
        COALESCE(us.total_xp, 0) as total_xp,
        COALESCE(us.level, 1) as level
    FROM "user" u
    LEFT JOIN careergoal cg ON u.id = cg.user_id
    LEFT JOIN habit h ON u.id = h.user_id
    LEFT JOIN userstats us ON u.id = us.user_id
    WHERE u.id = user_id_param
    GROUP BY u.id, us.total_xp, us.level;
END;
$$ LANGUAGE plpgsql;

-- Create indexes for better performance
-- Note: These would typically be created by Alembic migrations
-- But we'll add some basic ones here

-- Example: Create index on user_id for common queries
-- CREATE INDEX IF NOT EXISTS idx_career_goal_user_id ON careergoal(user_id);
-- CREATE INDEX IF NOT EXISTS idx_habit_user_id ON habit(user_id);
-- CREATE INDEX IF NOT EXISTS idx_expense_user_id ON expense(user_id);
-- CREATE INDEX IF NOT EXISTS idx_mood_log_user_id ON moodlog(user_id);

-- Note: The actual tables and indexes will be created by Alembic migrations
-- This script just sets up the initial database and any static data
