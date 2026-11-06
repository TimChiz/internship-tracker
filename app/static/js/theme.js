/**
 * Day and night mode for every page: remembers the visitor's choice and runs the sun/moon switch.
 * The choice carries over between pages.
 *
 * Why this file is loaded in the <head>: it applies the saved choice before the page is drawn,
 * so a night mode page never flashes in day colors while it loads.
 *
 * Any page that loads this file needs a button with id="theme-toggle". That button is the sun/moon switch.
 *
 * New to JavaScript? Here's what you need for this file:
 * - Everything here runs in the visitor's browser, not on our Python server.
 * - "const" creates a named value that never changes.
 * - "function" works like "def" in Python.
 * - "try / catch" works like "try / except" in Python.
 * - "condition ? a : b" means "a if condition else b" in Python.
 * - "===" means "is exactly equal to", like "==" in Python.
 * - "document" is the current page. document.getElementById("x") finds the HTML tag with id="x".
 * - addEventListener("click", someFunction) means "run someFunction whenever this is clicked".
 *   The function's name has no () after it, because the browser runs it later, not right now.
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

/**
 * Make the day/night switch's label say what clicking it will do next.
 */
function updateThemeToggleLabel() {
  const isNight = document.documentElement.dataset.theme === "night";
  const label = isNight ? "Switch to day mode" : "Switch to night mode";
  const themeToggle = document.getElementById("theme-toggle");

  // aria-label is what screen readers announce. title is the tooltip shown on hover.
  themeToggle.setAttribute("aria-label", label);
  themeToggle.setAttribute("title", label);
}

/**
 * Show the saved day/night choice. This also covers the browser's Back button,
 * which can restore an old copy of a page from before the choice changed.
 */
function applySavedTheme() {
  document.documentElement.dataset.theme = readSavedTheme();
  updateThemeToggleLabel();
}

/**
 * Switch the page between day and night, and remember the choice for other pages.
 */
function toggleTheme() {
  const root = document.documentElement;
  const nextTheme = root.dataset.theme === "night" ? "day" : "night";

  // Changing this attribute is all it takes to change the colors. The CSS does the rest.
  root.dataset.theme = nextTheme;
  saveTheme(nextTheme);
  updateThemeToggleLabel();
}

/**
 * Set the switch's label and make it respond to clicks. This waits for the page's HTML,
 * because this file runs in the <head>, before the switch exists.
 */
function connectThemeToggle() {
  updateThemeToggleLabel();
  document.getElementById("theme-toggle").addEventListener("click", toggleTheme);
}

// These lines run as soon as the browser loads the file.
// document.documentElement is the page's <html> tag, and dataset.theme is its data-theme attribute.
// tokens.css picks the day or night colors based on that attribute.
document.documentElement.dataset.theme = readSavedTheme();

// "DOMContentLoaded" happens once the page's HTML has been read, so the switch exists by then.
document.addEventListener("DOMContentLoaded", connectThemeToggle);

// "pageshow" happens whenever a page appears, including when someone returns with the Back button.
window.addEventListener("pageshow", applySavedTheme);
