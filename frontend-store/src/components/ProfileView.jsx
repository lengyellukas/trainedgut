export default function ProfileView({ email, onBack, onLogout }) {
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

        <div className="profile-empty">
          <p>Your athlete details will appear here after you generate a plan.</p>
          <p className="profile-empty-sub">
            Editable profile is coming in the next update.
          </p>
        </div>
      </main>
    </div>
  )
}
