// Adapted from Watermelon UI Continuous Tabs (MIT).
// https://registry.watermelon.sh/r/continuous-tabs.json
// Changes: controlled state, CSS tokens, unique layout group and accessible pressed buttons.
import { useId } from 'react';
import { LayoutGroup, motion } from 'motion/react';

export function ContinuousTabs({ options, value, onChange, label }) {
  const id = useId();
  return <LayoutGroup id={id}><nav className="continuous-tabs" aria-label={label}>
    {options.map(option => <button key={option} aria-pressed={value === option}
      onClick={() => onChange(option)} className={value === option ? 'selected' : ''}>
      {value === option && <motion.div layoutId="active-pill" className="active-pill"
        transition={{ type: 'spring', stiffness: 380, damping: 30, mass: 0.9 }} />}
      <motion.span layout="position">{option}</motion.span>
    </button>)}
  </nav></LayoutGroup>;
}
