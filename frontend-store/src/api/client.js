const API_BASE = import.meta.env.VITE_API_URL

export async function generatePlan(formData) {
  const payload = {
    body_weight_kg: parseFloat(formData.body_weight_kg),
    sport_type: formData.sport_type,
    target_race_time_hours: parseFloat(formData.target_race_time_hours),
    race_date: formData.race_date,
    start_preference: formData.start_preference,
    preferred_start_date: formData.preferred_start_date || null,
    carb_tolerance_option: formData.carb_tolerance_option,
    gi_history: formData.gi_history,
    long_sessions: formData.long_sessions.map(s => ({ duration_option: s.duration_option })),
  }

  const res = await fetch(`${API_BASE}/generate-plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Server error ${res.status}: ${text}`)
  }

  return res.json()
}
