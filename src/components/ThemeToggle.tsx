/**
 * Simple Theme Toggle Component
 * 
 * Following MANDATORY.md: Basic useState, simple UI, no complex patterns.
 */

import { useState, useEffect } from 'react';
import { 
  getStoredTheme, 
  saveTheme, 
  applyTheme, 
  getEffectiveTheme,
  setupSystemThemeListener,
  type Theme 
} from '../utils/theme';

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>('system');

  // Load theme on component mount
  useEffect(() => {
    const storedTheme = getStoredTheme();
    setTheme(storedTheme);
    applyTheme(storedTheme);
  }, []);

  // Listen for system theme changes when theme is 'system'
  useEffect(() => {
    if (theme === 'system') {
      const cleanup = setupSystemThemeListener(() => {
        // Re-apply system theme when system preference changes
        applyTheme('system');
      });
      return cleanup;
    }
  }, [theme]);

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    saveTheme(newTheme);
    applyTheme(newTheme);
  };

  const effectiveTheme = getEffectiveTheme(theme);

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm text-muted-foreground">Theme:</span>
      <select 
        value={theme}
        onChange={(e) => handleThemeChange(e.target.value as Theme)}
        className="text-sm border border-border rounded px-2 py-1 bg-background"
        aria-label="Select theme"
      >
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
      
      {/* Simple indicator */}
      <span className="text-xs text-muted-foreground">
        ({effectiveTheme === 'dark' ? '🌙' : '☀️'})
      </span>
    </div>
  );
}