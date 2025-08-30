import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Smile, 
  Meh, 
  Frown, 
  Battery, 
  Zap, 
  Coffee, 
  Heart, 
  Activity,
  Bed,
  Dumbbell
} from 'lucide-react';

const MoodTracker = ({
  onMoodSubmit,
  initialMood = null,
  initialEnergy = null,
  initialStress = null,
  initialSleep = null,
  initialExercise = null,
  className = ''
}) => {
  const [mood, setMood] = useState(initialMood);
  const [energy, setEnergy] = useState(initialEnergy);
  const [stress, setStress] = useState(initialStress);
  const [sleep, setSleep] = useState(initialSleep);
  const [exercise, setExercise] = useState(initialExercise);
  const [notes, setNotes] = useState('');

  const moodOptions = [
    { value: 1, icon: Frown, label: 'Very Sad', color: 'text-red-500', bgColor: 'bg-red-100' },
    { value: 2, icon: Frown, label: 'Sad', color: 'text-orange-500', bgColor: 'bg-orange-100' },
    { value: 3, icon: Meh, label: 'Okay', color: 'text-yellow-500', bgColor: 'bg-yellow-100' },
    { value: 4, icon: Meh, label: 'Good', color: 'text-blue-500', bgColor: 'bg-blue-100' },
    { value: 5, icon: Smile, label: 'Great', color: 'text-green-500', bgColor: 'bg-green-100' },
    { value: 6, icon: Smile, label: 'Excellent', color: 'text-emerald-500', bgColor: 'bg-emerald-100' },
    { value: 7, icon: Heart, label: 'Amazing', color: 'text-purple-500', bgColor: 'bg-purple-100' },
    { value: 8, icon: Heart, label: 'Fantastic', color: 'text-pink-500', bgColor: 'bg-pink-100' },
    { value: 9, icon: Heart, label: 'Incredible', color: 'text-indigo-500', bgColor: 'bg-indigo-100' },
    { value: 10, icon: Heart, label: 'Perfect', color: 'text-violet-500', bgColor: 'bg-violet-100' }
  ];

  const energyOptions = [
    { value: 1, icon: Battery, label: 'Very Low', color: 'text-red-500' },
    { value: 2, icon: Battery, label: 'Low', color: 'text-orange-500' },
    { value: 3, icon: Battery, label: 'Moderate', color: 'text-yellow-500' },
    { value: 4, icon: Zap, label: 'Good', color: 'text-blue-500' },
    { value: 5, icon: Zap, label: 'High', color: 'text-green-500' }
  ];

  const stressOptions = [
    { value: 1, icon: Coffee, label: 'Very Low', color: 'text-green-500' },
    { value: 2, icon: Coffee, label: 'Low', color: 'text-blue-500' },
    { value: 3, icon: Activity, label: 'Moderate', color: 'text-yellow-500' },
    { value: 4, icon: Activity, label: 'High', color: 'text-orange-500' },
    { value: 5, icon: Activity, label: 'Very High', color: 'text-red-500' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onMoodSubmit) {
      onMoodSubmit({
        mood_score: mood,
        energy_level: energy,
        stress_level: stress,
        sleep_hours: sleep,
        exercise_minutes: exercise,
        notes: notes.trim() || null
      });
    }
  };

  const isFormValid = mood !== null;

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">How are you feeling today?</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Mood Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Mood (1-10)
          </label>
          <div className="grid grid-cols-5 gap-2">
            {moodOptions.map((option) => {
              const Icon = option.icon;
              const isSelected = mood === option.value;
              
              return (
                <motion.button
                  key={option.value}
                  type="button"
                  onClick={() => setMood(option.value)}
                  className={`p-3 rounded-lg border-2 transition-all duration-200 ${
                    isSelected 
                      ? `${option.bgColor} border-${option.color.split('-')[1]}-300` 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Icon className={`w-6 h-6 mx-auto mb-1 ${option.color}`} />
                  <span className="text-xs text-gray-600 block">{option.value}</span>
                  <span className="text-xs text-gray-500 block truncate">{option.label}</span>
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Energy Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Energy Level (1-5)
          </label>
          <div className="flex space-x-2">
            {energyOptions.map((option) => {
              const Icon = option.icon;
              const isSelected = energy === option.value;
              
              return (
                <motion.button
                  key={option.value}
                  type="button"
                  onClick={() => setEnergy(option.value)}
                  className={`flex-1 p-3 rounded-lg border-2 transition-all duration-200 ${
                    isSelected 
                      ? 'bg-blue-100 border-blue-300' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Icon className={`w-5 h-5 mx-auto mb-1 ${option.color}`} />
                  <span className="text-xs text-gray-600 block">{option.value}</span>
                  <span className="text-xs text-gray-500 block truncate">{option.label}</span>
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Stress Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Stress Level (1-5)
          </label>
          <div className="flex space-x-2">
            {stressOptions.map((option) => {
              const Icon = option.icon;
              const isSelected = stress === option.value;
              
              return (
                <motion.button
                  key={option.value}
                  type="button"
                  onClick={() => setStress(option.value)}
                  className={`flex-1 p-3 rounded-lg border-2 transition-all duration-200 ${
                    isSelected 
                      ? 'bg-orange-100 border-orange-300' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Icon className={`w-5 h-5 mx-auto mb-1 ${option.color}`} />
                  <span className="text-xs text-gray-600 block">{option.value}</span>
                  <span className="text-xs text-gray-500 block truncate">{option.label}</span>
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Sleep and Exercise */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sleep Hours
            </label>
            <div className="flex items-center space-x-2">
              <Bed className="w-5 h-5 text-gray-400" />
              <input
                type="number"
                min="0"
                max="24"
                step="0.5"
                value={sleep || ''}
                onChange={(e) => setSleep(e.target.value ? parseFloat(e.target.value) : null)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="7.5"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Exercise (minutes)
            </label>
            <div className="flex items-center space-x-2">
              <Dumbbell className="w-5 h-5 text-gray-400" />
              <input
                type="number"
                min="0"
                max="300"
                step="5"
                value={exercise || ''}
                onChange={(e) => setExercise(e.target.value ? parseInt(e.target.value) : null)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="30"
              />
            </div>
          </div>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notes (optional)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="How was your day? Any specific thoughts or feelings?"
          />
        </div>

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={!isFormValid}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
            isFormValid
              ? 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-4 focus:ring-primary-200'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
          whileHover={isFormValid ? { scale: 1.02 } : {}}
          whileTap={isFormValid ? { scale: 0.98 } : {}}
        >
          Log Mood Entry
        </motion.button>
      </form>
    </div>
  );
};

export default MoodTracker;
