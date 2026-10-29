import { useId } from 'react';
import { LayoutGroup, motion } from 'motion/react';
import { Moon, Sun } from 'lucide-react';

export default function ThemeSwitch({ value, onChange }) {
  const id = useId();
  return <LayoutGroup id={id}><div className="theme-switch" role="group" aria-label="Color theme">
    {[['light', Sun, 'Light'], ['dark', Moon, 'Dark']].map(([theme, Icon, label]) =>
      <button key={theme} onClick={() => onChange(theme)} aria-label={`Use ${theme} theme`} aria-pressed={value === theme}>
        {value === theme && <motion.span className="theme-indicator" layoutId="theme-selection" transition={{ duration: .22, ease: [.2, .7, .2, 1] }}/>}
        <Icon size={16}/><span>{label}</span>
      </button>)}
  </div></LayoutGroup>;
}
