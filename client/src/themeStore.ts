export type Theme = 'light' | 'dark'

interface DomTarget {
  dataset: Record<string, string>
}

interface StorageTarget {
  getItem(key: string): string | null
  setItem(key: string, value: string): void
}

interface ThemeStoreOptions {
  dom: DomTarget
  storage: StorageTarget
  prefersDark: boolean
}

export interface ThemeStore {
  theme: Theme
  toggleTheme(): void
}

export function createThemeStore({ dom, storage, prefersDark }: ThemeStoreOptions): ThemeStore {
  const saved = storage.getItem('theme')
  let current: Theme = saved === 'light' || saved === 'dark'
    ? saved
    : prefersDark ? 'dark' : 'light'

  dom.dataset.theme = current

  function toggleTheme() {
    current = current === 'light' ? 'dark' : 'light'
    dom.dataset.theme = current
    storage.setItem('theme', current)
  }

  return {
    get theme() { return current },
    toggleTheme,
  }
}
