import { create } from 'zustand';

interface ThemeState {
  isDark: boolean;
  toggle: () => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  isDark: localStorage.getItem('arsa_theme') === 'dark',

  toggle: () =>
    set((state) => {
      const newDark = !state.isDark;
      localStorage.setItem('arsa_theme', newDark ? 'dark' : 'light');
      if (newDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return { isDark: newDark };
    }),
}));

// Initialize on load
if (localStorage.getItem('arsa_theme') === 'dark') {
  document.documentElement.classList.add('dark');
}
