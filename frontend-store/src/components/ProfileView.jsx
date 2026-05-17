function Row({ label, value }) {
  return (
    <div className="profile-row">
      <span className="profile-row-label">{label}</span>
      <span className="profile-row-value">{value ?? '-'}</span>
    </div>
  )
}

export default function ProfileView({ email, profile, onBack, onLogout }) {
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
            <Row label="Weight" value={profile.weight_kg != null ? `${profile.weight_kg} kg` : null} />
            <Row label="Height" value={profile.height_cm != null ? `${profile.height_cm} cm` : null} />
            <p className="profile-note">
              Captured from your most recent plan submission. Editable profile is coming in the next update.
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
