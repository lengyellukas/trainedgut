const DURATIONS = [
  { value: '90min_to_2h', label: '90 min – 2 h',  windows: '2 fueling windows' },
  { value: '2h_to_3h',   label: '2 – 3 h',        windows: '4 fueling windows' },
  { value: '3h_to_4h',   label: '3 – 4 h',        windows: '6 fueling windows' },
  { value: 'over_4h',    label: '4 h +',           windows: '8 fueling windows' },
]

export default function YourTraining({ data, update }) {
  const sessions = data.long_sessions

  function addSession() {
    update({ long_sessions: [...sessions, { duration_option: '' }] })
  }

  function removeSession(index) {
    update({ long_sessions: sessions.filter((_, i) => i !== index) })
  }

  function setDuration(index, value) {
    const updated = sessions.map((s, i) => i === index ? { ...s, duration_option: value } : s)
    update({ long_sessions: updated })
  }

  return (
    <div className="step-content">
      <p className="step-eyebrow">Step 3 of 5</p>
      <h1 className="step-title">Your Training</h1>
      <p className="step-subtitle">
        Which long sessions do you do each week? These are the only sessions where gut training matters —
        we'll build your gel schedule around them.
      </p>

      <div className="sessions-list">
        {sessions.map((session, i) => (
          <div key={i} className="session-card">
            <div className="session-header">
              <span className="session-label">Long Session {i + 1}</span>
              {sessions.length > 1 && (
                <button className="btn-remove" onClick={() => removeSession(i)} title="Remove session">×</button>
              )}
            </div>
            <div className="duration-options">
              {DURATIONS.map(d => (
                <button
                  key={d.value}
                  className={`duration-btn ${session.duration_option === d.value ? 'selected' : ''}`}
                  onClick={() => setDuration(i, d.value)}
                >
                  <div>{d.label}</div>
                  <div style={{ fontSize: 10, opacity: 0.6, marginTop: 3 }}>{d.windows}</div>
                </button>
              ))}
            </div>
          </div>
        ))}

        <button className="btn-add-session" onClick={addSession}>
          + Add another long session
        </button>
      </div>
    </div>
  )
}
