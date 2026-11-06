/**
 * Behavior for the log in and create account screens:
 * the day/night switch, the show/hide password buttons, and holding the form back until the auth backend exists.
 * Saving the day/night choice is handled by theme.js, which loads first, so its functions can be used here.
 *
 * New to JavaScript? Here's what you need for this file:
 * - Everything here runs in the visitor's browser, not on our Python server.
 * - "function" works like "def" in Python, and "const" creates a named value that never changes.
 * - "document" is the current page. document.getElementById("x") finds the HTML tag with id="x".
 * - "condition ? a : b" means "a if condition else b" in Python.
 * - "===" means "is exactly equal to", and "!" means "not".
 * - addEventListener("click", someFunction) means "run someFunction whenever this is clicked".
 *   The function's name has no () after it, because the browser runs it later, not right now.
 */

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
 * Show or hide the password next to the eye button, and swap the button's icon and label to match.
 * @param {MouseEvent} event - The click on the eye button. The browser passes this in automatically.
 */
function togglePasswordVisibility(event) {
  // The register page has two eye buttons, so first find which one was clicked, then the input beside it.
  const button = event.currentTarget;
  const input = button.parentElement.querySelector("input");
  const isNowVisible = input.type === "password";

  // A "password" input shows dots, and a "text" input shows the actual characters.
  input.type = isNowVisible ? "text" : "password";
  button.setAttribute("aria-label", isNowVisible ? "Hide password" : "Show password");

  // Each button holds two icons, and only one is visible at a time.
  button.querySelector('[data-password-icon="show"]').hidden = isNowVisible;
  button.querySelector('[data-password-icon="hide"]').hidden = !isNowVisible;
}

/**
 * Stop the form from submitting.
 * TODO: remove this once /login and /register can handle a submitted form.
 * @param {SubmitEvent} event - The form's submit event. The browser passes this in automatically.
 */
function holdFormSubmission(event) {
  event.preventDefault();
}

// Everything below runs once when the page loads. It sets the label and connects the functions above to the page.
updateThemeToggleLabel();

// "pageshow" happens whenever a page appears, including when someone returns with the Back button.
window.addEventListener("pageshow", applySavedTheme);
document.getElementById("theme-toggle").addEventListener("click", toggleTheme);
document.getElementById("auth-form").addEventListener("submit", holdFormSubmission);

// querySelectorAll finds every matching tag. This loop works like "for button in buttons:" in Python.
for (const button of document.querySelectorAll("[data-password-toggle]")) {
  button.addEventListener("click", togglePasswordVisibility);
}
