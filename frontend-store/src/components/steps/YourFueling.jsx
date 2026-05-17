const CARB_OPTIONS = [
  {
    value: 'never_used',
    icon: '🚫',
    label: "I don't use gels",
    desc: 'You never or rarely take carbohydrates during training or racing.',
  },
  {
    value: 'occasional_one_gel',
    icon: '🟡',
    label: 'Occasional - 1 gel',
    desc: 'You occasionally take a single gel (~20 g carbs/hr). It feels manageable.',
  },
  {
    value: 'regular_one_two',
    icon: '🟠',
    label: 'Regular - 1–2 gels',
    desc: 'You regularly take 1–2 gels per hour (~45 g carbs/hr) with no major issues.',
  },
  {
    value: 'comfortable_two_plus',
    icon: '🟢',
    label: 'Comfortable - 2+ gels',
    desc: 'You comfortably handle 2 or more gels per hour (~70 g carbs/hr).',
  },
]

const GI_OPTIONS = [
  {
    value: 'none',
    icon: '✅',
    label: 'No GI issues',
    desc: "You've never experienced nausea, bloating, or stomach cramps during exercise.",
  },
  {
    value: 'occasional',
    icon: '⚠️',
    label: 'Occasional issues',
    desc: 'You sometimes experience GI discomfort - nausea or cramps - but not every session.',
  },
  {
    value: 'frequent',
    icon: '🔴',
    label: 'Frequent issues',
    desc: 'GI distress is a regular problem during long training or racing. It affects your performance.',
  },
]

function OptionList({ options, selected, onSelect }) {
  return (
    <div className="option-grid" style={{ gridTemplateColumns: '1fr' }}>
      {options.map(o => (
        <button
          key={o.value}
          className={`option-card horizontal ${selected === o.value ? 'selected' : ''}`}
          onClick={() => onSelect(o.value)}
        >
          <span className="card-icon">{o.icon}</span>
          <span className="card-text">
            <span className="card-label">{o.label}</span>
            <span className="card-desc">{o.desc}</span>
          </span>
        </button>
      ))}
    </div>
  )
}

export default function YourFueling({ data, update, stepNumber, totalSteps }) {
  return (
    <div className="step-content">
      <p className="step-eyebrow">Step {stepNumber} of {totalSteps}</p>
      <h1 className="step-title">Your Fueling</h1>
      <p className="step-subtitle">
        This tells us where to start your protocol. Be honest - starting too high causes GI distress,
        starting too low just slows progress.
      </p>

      <div style={{ marginBottom: 28 }}>
        <p className="field-label" style={{ marginBottom: 10 }}>Current carb intake during exercise</p>
        <OptionList
          options={CARB_OPTIONS}
          selected={data.carb_tolerance_option}
          onSelect={v => update({ carb_tolerance_option: v })}
        />
        {!data.carb_tolerance_option && (
          <p className="field-error" style={{ marginTop: 8 }}>Select your current carb intake to continue.</p>
        )}
      </div>

      <div>
        <p className="field-label" style={{ marginBottom: 10 }}>GI distress history</p>
        <OptionList
          options={GI_OPTIONS}
          selected={data.gi_history}
          onSelect={v => update({ gi_history: v })}
        />
        {!data.gi_history && (
          <p className="field-error" style={{ marginTop: 8 }}>Select your GI distress history to continue.</p>
        )}
      </div>
    </div>
  )
}
