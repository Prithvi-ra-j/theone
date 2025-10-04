import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { miniAssistantAPI } from '../api'
import api from '../api/client'

export default function AssistantBuilder() {
  const qc = useQueryClient()
  const { data: assistant } = useQuery({
    queryKey: ['miniAssistant'],
    queryFn: miniAssistantAPI.getMiniAssistant
  })
  const [form, setForm] = useState({
    name: 'Astra',
    avatar: '🪔',
    personality: 'mentor',
    color_theme: 'blue',
    greeting_message: "Hi! I'm here to help.",
    preferences: { notifications: true },
    assistant_avatar: 'diya',
    assistant_personality: 'mentor',
    assistant_language: 'english'
  })

  useEffect(() => {
    if (assistant) {
      setForm((f) => ({
        ...f,
        name: assistant.name ?? f.name,
        avatar: assistant.avatar ?? f.avatar,
        personality: assistant.personality ?? f.personality,
        color_theme: assistant.color_theme ?? f.color_theme,
        greeting_message: assistant.greeting_message ?? f.greeting_message,
        preferences: assistant.preferences ?? f.preferences,
      }))
    }
  }, [assistant])

  const saveAssistant = useMutation({
    mutationFn: async (payload) => {
      if (assistant) return miniAssistantAPI.updateMiniAssistant(payload)
      return miniAssistantAPI.createMiniAssistant(payload)
    },
    onSuccess: () => qc.invalidateQueries(['miniAssistant'])
  })

  const saveProfile = useMutation({
    mutationFn: async (p) => api.put('/users/me', p),
  })

  const onSubmit = async (e) => {
    e.preventDefault()
    await saveAssistant.mutateAsync({
      name: form.name,
      avatar: form.avatar,
      personality: form.personality,
      color_theme: form.color_theme,
      greeting_message: form.greeting_message,
      preferences: form.preferences,
    })
    await saveProfile.mutateAsync({
      assistant_avatar: form.assistant_avatar,
      assistant_personality: form.assistant_personality,
      assistant_language: form.assistant_language,
    })
    // simple redirect
    window.location.href = '/dashboard'
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Assistant Builder</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Assistant Name</label>
            <input className="w-full border rounded px-3 py-2" value={form.name} onChange={(e)=>setForm({...form, name:e.target.value})} />
          </div>
          {/* Avatar input removed for now */}
          <div>
            <label className="block text-sm font-medium mb-1">Personality</label>
            <select className="w-full border rounded px-3 py-2" value={form.personality} onChange={(e)=>setForm({...form, personality:e.target.value})}>
              <option value="mentor">Mentor</option>
              <option value="motivator">Motivator</option>
              <option value="calm">Calm Guide</option>
              <option value="chill">Chill Buddy</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Color Theme</label>
            <select className="w-full border rounded px-3 py-2" value={form.color_theme} onChange={(e)=>setForm({...form, color_theme:e.target.value})}>
              <option value="blue">Blue</option>
              <option value="purple">Purple</option>
              <option value="green">Green</option>
              <option value="red">Red</option>
              <option value="orange">Orange</option>
            </select>
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium mb-1">Greeting Message</label>
            <textarea className="w-full border rounded px-3 py-2" rows={3} value={form.greeting_message} onChange={(e)=>setForm({...form, greeting_message:e.target.value})} />
          </div>
        </div>

        <div className="mt-6">
          <h2 className="font-semibold mb-2">Language & Personality</h2>
          <div className="grid grid-cols-3 gap-4">
            {/* Avatar preset removed for now */}
            <div>
              <label className="block text-sm font-medium mb-1">Personality preset</label>
              <select className="w-full border rounded px-3 py-2" value={form.assistant_personality} onChange={(e)=>setForm({...form, assistant_personality:e.target.value})}>
                <option value="mentor">Mentor</option>
                <option value="motivator">Motivator</option>
                <option value="calm">Calm</option>
                <option value="chill">Chill</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Language</label>
              <select className="w-full border rounded px-3 py-2" value={form.assistant_language} onChange={(e)=>setForm({...form, assistant_language:e.target.value})}>
                <option value="english">English</option>
                <option value="hindi">Hindi</option>
                <option value="hinglish">Hinglish</option>
                <option value="tamil">Tamil</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <a href="/dashboard" className="px-4 py-2 border rounded">Skip</a>
          <button type="submit" className="px-4 py-2 rounded text-white bg-blue-600">Save and Continue</button>
        </div>
      </form>
    </div>
  )
}
