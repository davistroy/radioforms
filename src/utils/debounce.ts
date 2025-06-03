/**
 * Simple debounce utility for emergency responder search
 * 
 * Following MANDATORY.md: Simple utility function under 20 lines
 * Prevents excessive API calls during typing
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: number | null = null;

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      window.clearTimeout(timeoutId);
    }
    
    timeoutId = window.setTimeout(() => {
      func(...args);
    }, delay);
  };
}