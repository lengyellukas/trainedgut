import { MARKETS, GEL_SOURCES } from '../../constants'

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

export default function YourGels({ data, update, stepNumber, totalSteps }) {
  return (
    <div className="step-content">
      <p className="step-eyebrow">Step {stepNumber} of {totalSteps}</p>
      <h1 className="step-title">Your Gels</h1>
      <p className="step-subtitle">
        Where the protocol gets its physical gels. You can switch between our own products and
        third-party brands sold locally.
      </p>

      {/* Shipping country */}
      <div style={{ marginBottom: 28 }}>
        <p className="field-label" style={{ marginBottom: 10 }}>Where will you train and receive your gels?</p>
        <div className="option-grid cols-3">
          {MARKETS.map(m => (
            <button
              key={m.value}
              className={`option-card ${data.market === m.value ? 'selected' : ''}`}
              onClick={() => update({ market: m.value })}
            >
              <span className="card-label">{m.label}</span>
            </button>
          ))}
        </div>
        {!data.market && (
          <p className="field-error" style={{ marginTop: 8 }}>Pick a country to filter gels available locally.</p>
        )}
      </div>

      {/* Gel source */}
      <div>
        <p className="field-label" style={{ marginBottom: 10 }}>Which gels would you like to use?</p>
        <OptionList
          options={GEL_SOURCES.map(s => ({
            value: s.value,
            icon: s.recommended ? '✨' : '🛒',
            label: s.label + (s.recommended ? ' - recommended' : ''),
            desc: s.desc,
          }))}
          selected={data.gel_brand}
          onSelect={v => update({ gel_brand: v })}
        />
        <p className="field-hint" style={{ marginTop: 6, fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>
          With third-party gels, the algorithm picks the best mix per ratio phase from brands available in your country. You may end up with gels from several brands across the plan.
        </p>
      </div>
    </div>
  )
}
