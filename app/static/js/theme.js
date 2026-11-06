/**
 * Remembers whether the visitor chose day or night mode, so the choice carries over between pages.
 *
 * Why this file is separate: layout.html loads it in the <head>, before the page is drawn.
 * That way, a night mode page never flashes in day colors while it loads.
 *
 * New to JavaScript? Here's what you need for this file:
 * - Everything here runs in the visitor's browser, not on our Python server.
 * - "const" creates a named value that never changes.
 * - "function" works like "def" in Python.
 * - "try / catch" works like "try / except" in Python.
 * - "condition ? a : b" means "a if condition else b" in Python.
 * - "===" means "is exactly equal to", like "==" in Python.
 * - localStorage is a small storage space in the browser. Saved values are still there on the next page.
 */

// The name the choice is saved under in localStorage, like a key in a Python dictionary.
const THEME_STORAGE_KEY = "rat-race-theme";

/**
 * Get the saved day/night choice. Day is the default, including when the browser blocks storage.
 * @returns {string} "night" or "day".
 */
function readSavedTheme() {
  // Some browser privacy settings block localStorage and cause an error, so we catch that error.
  try {
    // Only an exact "night" counts. Nothing saved yet, or anything unexpected, gives "day".
    return localStorage.getItem(THEME_STORAGE_KEY) === "night" ? "night" : "day";
  } catch {
    return "day";
  }
}

/**
 * Save the day/night choice for later pages. If the browser blocks storage, the choice lasts for this page only.
 * @param {string} theme - "night" or "day".
 */
function saveTheme(theme) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // The page still switches modes; the choice just can't be remembered.
  }
}

// This line runs as soon as the browser loads the file.
// document.documentElement is the page's <html> tag, and dataset.theme is its data-theme attribute.
// tokens.css picks the day or night colors based on that attribute.
document.documentElement.dataset.theme = readSavedTheme();
