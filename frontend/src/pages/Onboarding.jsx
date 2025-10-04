import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import usersAPI from '../api/users';
import Button from '../components/ui/Button.jsx';
import Select from '../components/ui/Select.jsx';
import Input from '../components/ui/Input.jsx';

const steps = ['Basics', 'Career', 'Location'];

export default function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: '',
    preferences: {
      branch: '',
      year: '',
      interests: [],
      target_role: '',
      location: 'India',
    },
  });

  useEffect(() => {
    // Try to load profile to prefill
    (async () => {
      try {
        const me = await usersAPI.me();
        setForm((f) => ({
          ...f,
          name: me?.name || f.name,
          preferences: { ...(me?.preferences || f.preferences) }
        }));
      } catch (_) {}
    })();
  }, []);

  const next = () => setStep((s) => Math.min(s + 1, steps.length - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));

  const updatePref = (key, value) => {
    setForm((f) => ({ ...f, preferences: { ...f.preferences, [key]: value } }));
  };

  const save = async () => {
    setSaving(true);
    try {
      await usersAPI.updateMe(form);
      // Also stash minimal snapshot locally for demo mode
      localStorage.setItem('onboarding_preferences', JSON.stringify(form.preferences));
      navigate('/dashboard');
    } catch (e) {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-1">Welcome to Dristhi</h1>
      <p className="text-gray-500 mb-6">Let’s personalize your experience (1–2 minutes)</p>

      <div className="mb-6">
        <div className="flex gap-2 text-sm">
          {steps.map((label, i) => (
            <div key={label} className={`flex-1 h-1 rounded ${i <= step ? 'bg-indigo-600' : 'bg-gray-200'}`} />
          ))}
        </div>
        <div className="mt-2 text-sm text-gray-600">Step {step + 1} of {steps.length}: {steps[step]}</div>
      </div>

      {step === 0 && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Your name</label>
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., Shruthi" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Branch</label>
            <Select value={form.preferences.branch} onChange={(e) => updatePref('branch', e.target.value)}>
              <option value="">Select</option>
              <option value="CSE">CSE</option>
              <option value="ECE">ECE</option>
              <option value="EEE">EEE</option>
              <option value="MECH">Mechanical</option>
              <option value="CIVIL">Civil</option>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Year</label>
            <Select value={form.preferences.year} onChange={(e) => updatePref('year', e.target.value)}>
              <option value="">Select</option>
              <option value="1">1st</option>
              <option value="2">2nd</option>
              <option value="3">3rd</option>
              <option value="4">4th</option>
            </Select>
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Target Role</label>
            <Input value={form.preferences.target_role} onChange={(e) => updatePref('target_role', e.target.value)} placeholder="e.g., Frontend Developer" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Interests (comma separated)</label>
            <Input value={form.preferences.interests?.join(', ') || ''} onChange={(e) => updatePref('interests', e.target.value.split(',').map(s => s.trim()).filter(Boolean))} placeholder="AI, Web, Systems" />
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Location</label>
            <Select value={form.preferences.location} onChange={(e) => updatePref('location', e.target.value)}>
              <option value="India">India</option>
              <option value="Remote">Remote</option>
              <option value="Other">Other</option>
            </Select>
          </div>
        </div>
      )}

      <div className="mt-8 flex justify-between">
        <Button variant="secondary" onClick={prev} disabled={step === 0}>Back</Button>
        {step < steps.length - 1 ? (
          <Button onClick={next}>Next</Button>
        ) : (
          <Button onClick={save} disabled={saving}>{saving ? 'Saving…' : 'Finish'}</Button>
        )}
      </div>
    </div>
  )
}
