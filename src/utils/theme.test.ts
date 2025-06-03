/**
 * Simple Theme Utility Tests
 * 
 * Following MANDATORY.md: Basic tests, no complex mocking.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { 
  getStoredTheme, 
  saveTheme, 
  systemPrefersDark, 
  getEffectiveTheme, 
  applyTheme,
  type Theme 
} from './theme';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock matchMedia
const matchMediaMock = vi.fn();
Object.defineProperty(window, 'matchMedia', { value: matchMediaMock });

describe('Theme Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset document.documentElement classList
    document.documentElement.className = '';
  });

  describe('getStoredTheme', () => {
    it('returns stored theme from localStorage', () => {
      localStorageMock.getItem.mockReturnValue('dark');
      expect(getStoredTheme()).toBe('dark');
    });

    it('returns system as default when no stored theme', () => {
      localStorageMock.getItem.mockReturnValue(null);
      expect(getStoredTheme()).toBe('system');
    });

    it('returns system when invalid theme stored', () => {
      localStorageMock.getItem.mockReturnValue('invalid');
      expect(getStoredTheme()).toBe('system');
    });

    it('handles localStorage errors gracefully', () => {
      localStorageMock.getItem.mockImplementation(() => {
        throw new Error('localStorage error');
      });
      expect(getStoredTheme()).toBe('system');
    });
  });

  describe('saveTheme', () => {
    it('saves theme to localStorage', () => {
      saveTheme('dark');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('radioforms-theme', 'dark');
    });

    it('handles localStorage errors gracefully', () => {
      localStorageMock.setItem.mockImplementation(() => {
        throw new Error('localStorage error');
      });
      expect(() => saveTheme('dark')).not.toThrow();
    });
  });

  describe('systemPrefersDark', () => {
    it('returns true when system prefers dark', () => {
      matchMediaMock.mockReturnValue({ matches: true });
      expect(systemPrefersDark()).toBe(true);
      expect(matchMediaMock).toHaveBeenCalledWith('(prefers-color-scheme: dark)');
    });

    it('returns false when system prefers light', () => {
      matchMediaMock.mockReturnValue({ matches: false });
      expect(systemPrefersDark()).toBe(false);
    });

    it('returns false when matchMedia not available', () => {
      Object.defineProperty(window, 'matchMedia', { value: undefined });
      expect(systemPrefersDark()).toBe(false);
    });
  });

  describe('getEffectiveTheme', () => {
    it('returns light for light theme', () => {
      expect(getEffectiveTheme('light')).toBe('light');
    });

    it('returns dark for dark theme', () => {
      expect(getEffectiveTheme('dark')).toBe('dark');
    });

    it('returns dark for system when system prefers dark', () => {
      matchMediaMock.mockReturnValue({ matches: true });
      expect(getEffectiveTheme('system')).toBe('dark');
    });

    it('returns light for system when system prefers light', () => {
      matchMediaMock.mockReturnValue({ matches: false });
      expect(getEffectiveTheme('system')).toBe('light');
    });
  });

  describe('applyTheme', () => {
    it('adds dark class for dark theme', () => {
      applyTheme('dark');
      expect(document.documentElement.classList.contains('dark')).toBe(true);
      expect(document.documentElement.classList.contains('light')).toBe(false);
    });

    it('adds light class for light theme', () => {
      applyTheme('light');
      expect(document.documentElement.classList.contains('light')).toBe(true);
      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });

    it('removes all theme classes for system theme', () => {
      document.documentElement.classList.add('dark', 'light');
      applyTheme('system');
      expect(document.documentElement.classList.contains('dark')).toBe(false);
      expect(document.documentElement.classList.contains('light')).toBe(false);
    });

    it('removes existing theme classes before applying new one', () => {
      document.documentElement.classList.add('light');
      applyTheme('dark');
      expect(document.documentElement.classList.contains('light')).toBe(false);
      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });
  });
});