export const FIELD_LIMITS = {
  age:            { min: 15,  max: 95,  label: 'Age',         unit: 'years' },
  body_weight_kg: { min: 30,  max: 250, label: 'Body weight',  unit: 'kg'    },
  height_cm:      { min: 100, max: 245, label: 'Height',       unit: 'cm'    },
}

// Countries where TrainedGut + partner gels are sold and shipped.
export const MARKETS = [
  { value: 'CH', label: 'Switzerland' },
  { value: 'CZ', label: 'Czech Republic' },
  { value: 'SK', label: 'Slovakia' },
]

// Source of the physical gels used in the plan. The selection algorithm
// picks brand-agnostic combinations per phase from whatever the source allows.
export const GEL_SOURCES = [
  {
    value: 'trainedgut',
    label: 'TrainedGut gels',
    desc: 'Recipes calibrated for the protocol. Shipped to your door.',
    recommended: true,
  },
  {
    value: 'third_party',
    label: 'Third-party gels from local shops',
    desc: 'Mix any brand sold in your country. Useful if you already buy gels you trust.',
  },
]
