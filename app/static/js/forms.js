const MESSAGES = {
  valueMissing: "Заполните это поле",
  tooShort: (el) => "Минимум символов: " + el.minLength,
  patternMismatch: "Допустимы латинские буквы, цифры и подчёркивание",
  typeMismatch: "Проверьте формат значения",
  rangeUnderflow: (el) => "Не меньше " + el.min,
  rangeOverflow: (el) => "Не больше " + el.max,
};

function messageFor(el) {
  for (const key of Object.keys(MESSAGES)) {
    if (el.validity[key]) {
      const m = MESSAGES[key];
      return typeof m === "function" ? m(el) : m;
    }
  }
  return "";
}

function showError(el, text) {
  const label = el.closest("label");
  let box = label.querySelector(".err.js");
  if (!text) {
    if (box) box.remove();
    el.removeAttribute("aria-invalid");
    return;
  }
  if (!box) {
    box = document.createElement("span");
    box.className = "err js";
    label.appendChild(box);
  }
  box.textContent = text;
  el.setAttribute("aria-invalid", "true");
}

document.querySelectorAll("form[data-validate]").forEach((form) => {
  const fields = form.querySelectorAll("input:not([type=hidden]), select, textarea");
  fields.forEach((el) => {
    el.addEventListener("blur", () => showError(el, el.validity.valid ? "" : messageFor(el)));
    el.addEventListener("input", () => {
      if (el.getAttribute("aria-invalid")) showError(el, el.validity.valid ? "" : messageFor(el));
    });
  });
  form.addEventListener("submit", (e) => {
    let first = null;
    fields.forEach((el) => {
      const bad = !el.validity.valid;
      showError(el, bad ? messageFor(el) : "");
      if (bad && !first) first = el;
    });
    if (first) {
      e.preventDefault();
      first.focus();
    }
  });
});
