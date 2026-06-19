import { useState, type ReactNode } from "react";
import { createThemeStore } from "./themeStore";
import { ThemeContext } from "./ThemeContext";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [store] = useState(() =>
    createThemeStore({
      dom: document.documentElement as unknown as {
        dataset: Record<string, string>;
      },
      storage: localStorage,
      prefersDark: window.matchMedia("(prefers-color-scheme: dark)").matches,
    }),
  );

  const [theme, setTheme] = useState(store.theme);

  function toggleTheme() {
    store.toggleTheme();
    setTheme(store.theme);
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
