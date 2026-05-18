import { supabase } from '../supabase'

const API_BASE = import.meta.env.VITE_API_URL

async function authHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.access_token) {
    throw new Error('Not signed in')
  }
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${session.access_token}`,
  }
}

async function request(method, path, body) {
  const headers = await authHeaders()
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Server error ${res.status}: ${text}`)
  }

  // 204 No Content has no body
  if (res.status === 204) return null
  return res.json()
}

export async function getMe() {
  return request('GET', '/me')
}

export async function updateProfile(updates) {
  return request('PATCH', '/me', updates)
}

export async function getActivePlan() {
  return request('GET', '/plan')
}

export async function deleteActivePlan() {
  return request('DELETE', '/plan')
}

export async function emailActivePlan({ weekNumber } = {}) {
  const qs = weekNumber != null ? `?week_number=${encodeURIComponent(weekNumber)}` : ''
  return request('POST', `/plan/email${qs}`)
}

export async function generatePlan(formData) {
  return request('POST', '/generate-plan', {
    body_weight_kg: parseFloat(formData.body_weight_kg),
    sport_type: formData.sport_type,
    target_race_time_hours: parseFloat(formData.target_race_time_hours),
    race_date: formData.race_date,
    start_preference: formData.start_preference,
    preferred_start_date: formData.preferred_start_date || null,
    carb_tolerance_option: formData.carb_tolerance_option,
    gi_history: formData.gi_history,
    long_sessions: formData.long_sessions.map(s => ({ duration_option: s.duration_option })),
    gel_brand: formData.gel_brand || 'trainedgut',
    market: formData.market || null,
    birth_year: formData.birth_year ? parseInt(formData.birth_year, 10) : null,
    height_cm: formData.height_cm ? parseInt(formData.height_cm, 10) : null,
  })
}

export async function submitFeedback(payload) {
  return request('POST', '/feedback', payload)
}

export async function submitExtraSession(payload) {
  return request('POST', '/extra-session', payload)
}

export async function getExtraSessions() {
  return request('GET', '/extra-sessions')
}
