// Served at /static/js/main.js and linked from templates/base.html.
console.log("QueuExpress loaded");

const joinForm = document.getElementById("join-form");
if (joinForm) {
  const button = joinForm.querySelector("button[type=submit]");
  const originalText = button.textContent;

  joinForm.addEventListener("submit", () => {
    button.disabled = true;
    button.textContent = "Getting your ticket…";
  });

  // If the person taps the browser's Back button, don't leave the button stuck.
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
      button.disabled = false;
      button.textContent = originalText;
    }
  });
}