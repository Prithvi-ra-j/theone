import { z } from 'zod';

export const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email'),
  bio: z.string().optional(),
  location: z.string().optional(),
  website: z.string().url('Please enter a valid URL').optional().or(z.literal('')),
  phone: z.string().optional(),
});

export const passwordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'New password must be at least 8 characters'),
  confirm_password: z.string().min(1, 'Please confirm your new password')
}).refine(data => data.new_password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password']
});

export const preferencesSchema = z.object({
  theme: z.enum(['light', 'dark', 'auto']),
  language: z.enum(['en', 'hi', 'ta', 'te', 'bn']),
  timezone: z.string(),
  daily_tips_enabled: z.boolean(),
  notification_style: z.enum(['gentle', 'moderate', 'aggressive']),
  hybrid_roadmap_choice: z.enum(['both', 'traditional', 'ai']),
});