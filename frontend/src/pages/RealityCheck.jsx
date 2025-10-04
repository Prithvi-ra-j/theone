import { useEffect, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { careerAPI } from '../api'
import { useSearchParams } from 'react-router-dom'

export default function RealityCheck() {
  const [searchParams] = useSearchParams()
  const [form, setForm] = useState({
    career_path: 'Software Engineer',
    education_level: 'B.Tech',
    location: 'Bengaluru',
    investment_amount: 400000,
    investment_time_years: 4,
  })

  useEffect(() => {
    const prefill = searchParams.get('career_path')
    if (prefill) setForm((f) => ({ ...f, career_path: prefill }))
  }, [searchParams])

  const rc = useMutation({
    mutationFn: (p) => careerAPI.realityCheck(p),
  })

  const onSubmit = async (e) => {
    e.preventDefault()
    await rc.mutateAsync(form)
  }

  return (
    <div className="max-w-2xl mx-auto p-6 text-gray-900 dark:text-gray-100">
      <h1 className="text-2xl font-bold mb-4">Reality Check Calculator</h1>
      <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
        Get a quick 5-year projection for a target career. Tip: Investment is your estimated spend on upskilling
        (courses, certifications, laptop, exams) over the period. Use ballpark numbers—you can refine later.
      </p>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Career Path</label>
            <input className="w-full border rounded px-3 py-2 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700" value={form.career_path} onChange={(e)=>setForm({...form, career_path: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Education Level</label>
            <input className="w-full border rounded px-3 py-2 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700" value={form.education_level} onChange={(e)=>setForm({...form, education_level: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Location</label>
            <input className="w-full border rounded px-3 py-2 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700" value={form.location} onChange={(e)=>setForm({...form, location: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Investment Amount (INR)</label>
            <input type="number" className="w-full border rounded px-3 py-2 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700" value={form.investment_amount} onChange={(e)=>setForm({...form, investment_amount: Number(e.target.value)})} />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Include courses, exams, devices, commuting. Example: 1–2 Lakh/year for 2–4 years.</p>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Investment Time (years)</label>
            <input type="number" className="w-full border rounded px-3 py-2 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700" value={form.investment_time_years} onChange={(e)=>setForm({...form, investment_time_years: Number(e.target.value)})} />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">How long you plan to actively invest in upskilling.</p>
          </div>
        </div>
        <div className="flex justify-end gap-2">
          <button type="submit" className="px-4 py-2 rounded text-white bg-green-600 hover:bg-green-700" disabled={rc.isPending}>{rc.isPending ? 'Calculating…' : 'Calculate'}</button>
        </div>
      </form>

      {rc.data && (
        <div className="mt-6 p-4 border rounded bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700">
          <h2 className="font-semibold mb-2">Result</h2>
          <p className="mb-1">ROI: <strong>{rc.data.roi_percentage.toFixed(0)}%</strong></p>
          <p className="mb-3">Projected 5-year Salary: <strong>{rc.data.projected_salary_5_years.toFixed(1)} LPA</strong></p>
          {/* Simple visualization: yearly investment vs projected salary growth (heuristic) */}
          <div className="h-64 mb-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={Array.from({ length: 6 }, (_, i) => {
                  const year = i; // 0..5
                  const investPerYear = (form.investment_amount || 0) / Math.max(1, form.investment_time_years || 1);
                  // Heuristic salary growth toward 5-year projection
                  const salary = (rc.data.projected_salary_5_years || 0) * (year / 5);
                  const invested = Math.min(year, form.investment_time_years || 0) * (investPerYear / 100000); // show in Lakh
                  return { year: `Y${year}`, SalaryLPA: salary, InvestedL: invested };
                })}
                margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="SalaryLPA" stroke="#3b82f6" strokeWidth={2} dot={false} name="Salary (LPA)" />
                <Line type="monotone" dataKey="InvestedL" stroke="#10b981" strokeWidth={2} dot={false} name="Invested (Lakh)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mb-3">
            <h3 className="font-medium">Challenges</h3>
            <ul className="list-disc ml-5">
              {rc.data.challenges.map((c, i) => <li key={i}>{c}</li>)}
            </ul>
          </div>
          <div className="mb-3">
            <h3 className="font-medium">Alternatives</h3>
            <ul className="list-disc ml-5">
              {rc.data.alternatives.map((c, i) => <li key={i}>{c}</li>)}
            </ul>
          </div>
          <p className="text-gray-700 dark:text-gray-300">{rc.data.ai_summary}</p>
        </div>
      )}
    </div>
  )
}
