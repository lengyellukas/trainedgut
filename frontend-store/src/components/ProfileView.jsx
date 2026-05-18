import { useState } from 'react'
import { updateProfile } from '../api/client'

function Row({ label, value, children }) {
  return (
    <div className="profile-row">
      <span className="profile-row-label">{label}</span>
      {children ?? <span className="profile-row-value">{value ?? '-'}</span>}
    </div>
  )
}

function WeightRow({ profile, onProfileChange, onShowToast }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState('')
  const [saving, setSaving] = useState(false)

  function start() {
    setDraft(profile?.weight_kg != null ? String(profile.weight_kg) : '')
    setEditing(true)
  }

  function cancel() {
    setEditing(false)
    setDraft('')
  }

  async function save() {
    const value = parseFloat(draft)
    if (Number.isNaN(value) || value < 30 || value > 250) {
      onShowToast?.('Weight must be a number between 30 and 250 kg.', 'error')
      return
    }
    setSaving(true)
    try {
      const updated = await updateProfile({ weight_kg: value })
      onProfileChange?.(updated)
      onShowToast?.(`Weight updated to ${value} kg.`, 'success')
      setEditing(false)
    } catch (err) {
      onShowToast?.(`Could not update weight. ${err.message || ''}`, 'error')
    } finally {
      setSaving(false)
    }
  }

  if (editing) {
    return (
      <div className="profile-row">
        <span className="profile-row-label">Weight</span>
        <span className="profile-edit-wrap">
          <input
            className="profile-edit-input"
            type="number"
            min="30"
            max="250"
            step="0.1"
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') save(); if (e.key === 'Escape') cancel() }}
            autoFocus
          />
          <span className="profile-edit-unit">kg</span>
          <button className="profile-edit-btn save" onClick={save} disabled={saving}>
            {saving ? '…' : 'Save'}
          </button>
          <button className="profile-edit-btn cancel" onClick={cancel} disabled={saving}>
            Cancel
          </button>
        </span>
      </div>
    )
  }

  return (
    <div className="profile-row">
      <span className="profile-row-label">Weight</span>
      <span className="profile-row-value">
        {profile?.weight_kg != null ? `${profile.weight_kg} kg` : '-'}
        <button className="profile-edit-pencil" onClick={start} title="Edit weight">✎</button>
      </span>
    </div>
  )
}

export default function ProfileView({ email, profile, onProfileChange, onShowToast, onBack, onLogout }) {
  // Athlete row exists from /me lazy-create, but biometric fields are only
  // populated after a plan is generated. Treat all-null as "empty".
  const hasAnyAthleteData =
    profile && (profile.birth_year != null || profile.weight_kg != null || profile.height_cm != null)

  return (
    <div className="menu-shell">
      <header className="menu-header">
        <span className="store-logo">Trained<span>Gut</span></span>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn-logout" onClick={onBack}>← Menu</button>
          <button className="btn-logout" onClick={onLogout} title={email}>Log out</button>
        </div>
      </header>

      <main className="menu-main">
        <h1 className="menu-tagline">Profile</h1>
        <p className="menu-user">Signed in as <span>{email}</span></p>

        {hasAnyAthleteData ? (
          <div className="profile-card">
            <Row label="Email" value={email} />
            <Row
              label="Birth year"
              value={profile.birth_year != null
                ? `${profile.birth_year}${profile.age != null ? ` (age ${profile.age})` : ''}`
                : null}
            />
            <WeightRow profile={profile} onProfileChange={onProfileChange} onShowToast={onShowToast} />
            <Row label="Height" value={profile.height_cm != null ? `${profile.height_cm} cm` : null} />
            <p className="profile-note">
              Captured from your most recent plan submission. Only weight is editable - other fields
              would require regenerating the plan.
            </p>
          </div>
        ) : (
          <div className="profile-empty">
            <p>Your athlete details will appear here after you generate a plan.</p>
            <p className="profile-empty-sub">
              Editable profile is coming in the next update.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
