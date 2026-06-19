import { Moon, Sun } from 'lucide-react'
import { useTheme } from './useTheme'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <button
      id="theme-toggle"
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '6px 12px',
        borderRadius: '999px',
        border: '1px solid var(--color-border)',
        background: 'var(--color-muted)',
        color: 'var(--color-foreground)',
        cursor: 'pointer',
        fontSize: '13px',
        fontWeight: 500,
        transition: 'background 0.2s, border-color 0.2s',
      }}
    >
      {isDark ? <Sun size={15} /> : <Moon size={15} />}
      {isDark ? 'Light' : 'Dark'}
    </button>
  )
}
