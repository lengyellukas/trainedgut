import { useState } from 'react'

const DURATIONS = [
  { value: '90min_to_2h', label: '90 min – 2 h' },
  { value: '2h_to_3h',   label: '2 – 3 h'       },
  { value: '3h_to_4h',   label: '3 – 4 h'       },
  { value: '4h_to_6h',   label: '4 – 6 h'       },
  { value: 'over_6h',    label: '6 h +'          },
]

export default function YourTraining({ data, update }) {
  const [touched, setTouched] = useState(false)
  const sessions = data.long_sessions

  function addSession() {
    setTouched(true)
    update({ long_sessions: [...sessions, { duration_option: '' }] })
  }

  function removeSession(index) {
    update({ long_sessions: sessions.filter((_, i) => i !== index) })
  }

  function setDuration(index, value) {
    setTouched(true)
    const updated = sessions.map((s, i) => i === index ? { ...s, duration_option: value } : s)
    update({ long_sessions: updated })
  }

  return (
    <div className="step-content">
      <p className="step-eyebrow">Step 3 of 5</p>
      <h1 className="step-title">Your Training</h1>
      <p className="step-subtitle">
        Which primary long sessions do you do in a typical training week? These are the sessions where gut training matters -
        we'll build your gel schedule around them. You can log unplanned or skipped sessions later, week by week.
      </p>

      <div className="sessions-list">
        {sessions.map((session, i) => (
          <div key={i} className="session-card">
            <div className="session-header">
              <span className="session-label">Primary Long Session {i + 1}</span>
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
                </button>
              ))}
            </div>
            {!session.duration_option && (
              <p className="field-error" style={{ marginTop: 8 }}>
                {touched ? 'Please select a duration for this session.' : 'Select a duration to continue.'}
              </p>
            )}
          </div>
        ))}

        <button className="btn-add-session" onClick={addSession}>
          + Add another primary long session
        </button>
      </div>
    </div>
  )
}
