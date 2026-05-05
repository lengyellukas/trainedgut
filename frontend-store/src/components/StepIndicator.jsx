export default function StepIndicator({ steps, current }) {
  return (
    <nav className="step-indicator">
      {steps.map((step, i) => {
        const state = i < current ? 'done' : i === current ? 'active' : 'pending'
        return (
          <div key={step.id} className="step-item">
            {i > 0 && <div className={`step-connector ${i <= current ? 'done' : ''}`} />}
            <div className={`step-dot ${state}`}>
              {i < current ? '✓' : i + 1}
            </div>
            <span className={`step-label ${state}`}>{step.label}</span>
          </div>
        )
      })}
    </nav>
  )
}
