import React from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import journalAPI from '../api/journal'
import { formatDistanceToNow } from 'date-fns'
import { Plus, Trash2, BookOpen, BarChart2, Tag, Smile, Frown, Meh } from 'lucide-react'

const moodBadge = (m) => {
  if (m == null) return 'bg-gray-100 text-gray-700'
  if (m >= 2) return 'bg-green-100 text-green-700'
  if (m <= -2) return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

const moodIcon = (m) => {
  if (m == null) return <Meh className="w-4 h-4" />
  if (m >= 2) return <Smile className="w-4 h-4" />
  if (m <= -2) return <Frown className="w-4 h-4" />
  return <Meh className="w-4 h-4" />
}

// Emoji-based mood picker (-5..5) with a simple popover
function MoodPicker({ value, onChange }) {
  const [open, setOpen] = React.useState(false)
  const ref = React.useRef(null)

  const moods = [
    { v: -5, e: '😭', label: 'Devastated' },
    { v: -4, e: '😢', label: 'Very sad' },
    { v: -3, e: '😞', label: 'Sad' },
    { v: -2, e: '😔', label: 'Down' },
    { v: -1, e: '🙁', label: 'Low' },
    { v:  0, e: '😐', label: 'Neutral' },
    { v:  1, e: '🙂', label: 'Okay' },
    { v:  2, e: '😊', label: 'Good' },
    { v:  3, e: '😀', label: 'Happy' },
    { v:  4, e: '😄', label: 'Very happy' },
    { v:  5, e: '🤩', label: 'Elated' },
  ]

  const current = moods.find(m => m.v === value)

  React.useEffect(() => {
    const onDocClick = (e) => {
      if (!open) return
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [open])

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        aria-haspopup="dialog"
        aria-expanded={open}
        className="inline-flex items-center gap-2 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-700"
        title="Select mood"
      >
        <span className="text-lg">
          {current ? current.e : '😐'}
        </span>
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {current ? `${current.label} (${current.v})` : 'Mood'}
        </span>
      </button>
      {open && (
        <div
          role="dialog"
          aria-label="Select mood"
          className="absolute z-50 mt-2 w-72 p-3 rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg"
        >
          <div className="grid grid-cols-6 gap-2">
            {moods.map(m => (
              <button
                key={m.v}
                type="button"
                onClick={() => { onChange(m.v); setOpen(false) }}
                className={`flex flex-col items-center justify-center p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 ${value === m.v ? 'ring-2 ring-primary-500' : ''}`}
                title={`${m.label} (${m.v})`}
              >
                <span className="text-xl leading-none">{m.e}</span>
                <span className="text-[10px] text-gray-500 mt-1">{m.v}</span>
              </button>
            ))}
          </div>
          <div className="mt-3 flex justify-between items-center">
            <div className="text-xs text-gray-500">Scale: -5 (low) to 5 (high)</div>
            <button
              type="button"
              onClick={() => { onChange(null); setOpen(false) }}
              className="text-xs text-gray-600 dark:text-gray-300 hover:underline"
            >
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function Journal() {
  const qc = useQueryClient()
  const [content, setContent] = React.useState('')
  const [tags, setTags] = React.useState('')
  const [userMood, setUserMood] = React.useState(0)

  const { data: entries, isLoading: loadingEntries } = useQuery({
    queryKey: ['journal','entries'],
    queryFn: () => journalAPI.listEntries({ limit: 50 }),
  })
  const { data: summary, isLoading: loadingSummary } = useQuery({
    queryKey: ['journal','summary',7],
    queryFn: () => journalAPI.getSummary(7),
  })

  const createMut = useMutation({
    mutationFn: (payload) => journalAPI.createEntry(payload),
    onSuccess: () => {
      toast.success('Journal entry added')
      setContent('')
      setTags('')
      setUserMood(0)
      qc.invalidateQueries(['journal'])
    },
    onError: () => toast.error('Failed to add entry'),
  })

  const delMut = useMutation({
    mutationFn: (id) => journalAPI.deleteEntry(id),
    onSuccess: () => {
      toast.success('Deleted entry')
      qc.invalidateQueries(['journal'])
    },
    onError: () => toast.error('Failed to delete'),
  })

  const onSubmit = (e) => {
    e.preventDefault()
    const payload = {
      content: content.trim(),
      tags: tags.split(',').map(t => t.trim()).filter(Boolean),
      user_mood: Number.isFinite(userMood) ? userMood : 0,
      is_private: true,
    }
    if (!payload.content) {
      toast.error('Write something first')
      return
    }
    createMut.mutate(payload)
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">Journal & Mood</h1>
          <p className="text-sm text-gray-500">Reflect daily. Get AI insights automatically.</p>
        </div>
      </header>

      <section className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
        <form onSubmit={onSubmit} className="p-4 space-y-3">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            placeholder="What’s on your mind today?"
            className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-transparent p-3 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
            <div className="flex gap-3 w-full sm:w-auto">
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="tags (comma separated)"
                className="flex-1 sm:w-72 rounded-md border border-gray-300 dark:border-gray-600 bg-transparent p-2"
              />
              <MoodPicker value={userMood} onChange={(v) => setUserMood(typeof v === 'number' ? v : 0)} />
            </div>
            <button
              type="submit"
              disabled={createMut.isLoading}
              className="inline-flex items-center gap-2 px-3 py-2 rounded-md bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50"
            >
              <Plus className="w-4 h-4" /> Add entry
            </button>
          </div>
        </form>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-3">
          <h2 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2"><BookOpen className="w-4 h-4"/>Recent entries</h2>
          <div className="space-y-3">
            {loadingEntries && <div className="text-sm text-gray-500">Loading entries…</div>}
            {entries?.length === 0 && <div className="text-sm text-gray-500">No entries yet. Write your first reflection above.</div>}
            {entries?.map(e => (
              <article key={e.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2 text-xs">
                    <span className={`px-2 py-0.5 rounded-full ${moodBadge(e.user_mood)}`}>{moodIcon(e.user_mood)}</span>
                    <span className="text-gray-500">{formatDistanceToNow(new Date(e.created_at))} ago</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => delMut.mutate(e.id)}
                    className="text-red-600 hover:text-red-700"
                    title="Delete entry"
                  >
                    <Trash2 className="w-4 h-4"/>
                  </button>
                </div>
                <p className="mt-2 text-gray-800 dark:text-gray-100 whitespace-pre-wrap">{e.content}</p>
                {e.tags?.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {e.tags.map((t, i) => (
                      <span key={i} className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200"><Tag className="w-3 h-3"/>{t}</span>
                    ))}
                  </div>
                )}
                {e.analysis && (
                  <div className="mt-3 text-sm text-gray-600 dark:text-gray-300">
                    <div className="font-medium">AI insights</div>
                    {e.analysis.summary && <p className="mt-1">Summary: {e.analysis.summary}</p>}
                    {Array.isArray(e.analysis.topics) && e.analysis.topics.length>0 && (
                      <p className="mt-1">Topics: {e.analysis.topics.join(', ')}</p>
                    )}
                    {Array.isArray(e.analysis.triggers) && e.analysis.triggers.length>0 && (
                      <p className="mt-1">Triggers: {e.analysis.triggers.join(', ')}</p>
                    )}
                  </div>
                )}
              </article>
            ))}
          </div>
        </div>
        <aside className="space-y-3">
          <h2 className="font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2"><BarChart2 className="w-4 h-4"/>Weekly summary</h2>
          <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800">
            {loadingSummary && <div className="text-sm text-gray-500">Loading…</div>}
            {summary && (
              <div className="space-y-2 text-sm">
                <div>Entries: <span className="font-medium">{summary.count}</span></div>
                <div>Avg mood: <span className="font-medium">{summary.avg_mood ?? '—'}</span></div>
                <div>
                  Top emotions:
                  <ul className="list-disc ml-5">
                    {summary.top_emotions?.map(([lab, cnt], i) => (
                      <li key={i}>{lab} <span className="text-xs text-gray-500">({cnt})</span></li>
                    ))}
                    {(!summary.top_emotions || summary.top_emotions.length===0) && <li className="text-gray-500">—</li>}
                  </ul>
                </div>
                <div>
                  Top topics:
                  <ul className="list-disc ml-5">
                    {summary.top_topics?.map(([lab, cnt], i) => (
                      <li key={i}>{lab} <span className="text-xs text-gray-500">({cnt})</span></li>
                    ))}
                    {(!summary.top_topics || summary.top_topics.length===0) && <li className="text-gray-500">—</li>}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </aside>
      </section>
    </div>
  )
}
