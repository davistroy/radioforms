/**
 * Simple Theme Utilities for RadioForms
 * 
 * Following MANDATORY.md: Simple functions, no complex state management or abstractions.
 * Just basic light/dark theme switching with localStorage.
 */

export type Theme = 'light' | 'dark' | 'system';

/**
 * Get the current theme from localStorage or default to 'system'
 */
export function getStoredTheme(): Theme {
  try {
    const stored = localStorage.getItem('radioforms-theme');
    if (stored === 'light' || stored === 'dark' || stored === 'system') {
      return stored;
    }
  } catch (error) {
    // localStorage might not be available
    console.warn('Could not access localStorage for theme');
  }
  return 'system';
}

/**
 * Save theme preference to localStorage
 */
export function saveTheme(theme: Theme): void {
  try {
    localStorage.setItem('radioforms-theme', theme);
  } catch (error) {
    console.warn('Could not save theme to localStorage');
  }
}

/**
 * Check if the system prefers dark mode
 */
export function systemPrefersDark(): boolean {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  return false;
}

/**
 * Get the effective theme (resolve 'system' to 'light' or 'dark')
 */
export function getEffectiveTheme(theme: Theme): 'light' | 'dark' {
  if (theme === 'system') {
    return systemPrefersDark() ? 'dark' : 'light';
  }
  return theme;
}

/**
 * Apply theme to the document root element
 */
export function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  
  // Remove existing theme classes
  root.classList.remove('light', 'dark');
  
  if (theme !== 'system') {
    // Add specific theme class
    root.classList.add(theme);
  }
  // For 'system', don't add any class - let CSS media query handle it
}

/**
 * Set up system theme change listener
 */
export function setupSystemThemeListener(callback: () => void): () => void {
  if (typeof window !== 'undefined' && window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handler = () => callback();
    mediaQuery.addEventListener('change', handler);
    
    // Return cleanup function
    return () => mediaQuery.removeEventListener('change', handler);
  }
  
  // Return no-op cleanup if not supported
  return () => {};
}