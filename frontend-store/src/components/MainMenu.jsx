function MenuCard({ title, description, onClick, disabled, soon }) {
  return (
    <button
      className={`menu-card ${disabled ? 'menu-card--disabled' : ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      <div className="menu-card-text">
        <div className="menu-card-title">
          {title}
          {soon && <span className="menu-card-soon">SOON</span>}
        </div>
        <div className="menu-card-desc">{description}</div>
      </div>
      <span className="menu-card-arrow">→</span>
    </button>
  )
}

export default function MainMenu({ email, hasPlan, onSelect, onLogout }) {
  return (
    <div className="menu-shell">
      <header className="menu-header">
        <span className="store-logo">Trained<span>Gut</span></span>
        <button className="btn-logout" onClick={onLogout} title={email}>
          Log out
        </button>
      </header>

      <main className="menu-main">
        <h1 className="menu-tagline">
          Train your gut, <span>fuel your race.</span>
        </h1>
        <p className="menu-user">Signed in as <span>{email}</span></p>

        <div className="menu-cards">
          <MenuCard
            title="Generate plan"
            description="Build a personalised gut training protocol for your next race."
            onClick={() => onSelect('form')}
            disabled={hasPlan}
          />
          <MenuCard
            title="Current plan"
            description={hasPlan ? "View your active plan and log session feedback." : "No active plan yet — generate one to get started."}
            onClick={() => onSelect('plan')}
            disabled={!hasPlan}
          />
          <MenuCard
            title="Profile"
            description="Your athlete details captured during plan generation."
            onClick={() => onSelect('profile')}
          />
          <MenuCard
            title="Past plans"
            description="Plans you've completed or canceled."
            onClick={() => {}}
            disabled
            soon
          />
        </div>

        {hasPlan && (
          <p className="menu-hint">
            To generate a new plan, cancel your active plan first.
          </p>
        )}
      </main>
    </div>
  )
}
