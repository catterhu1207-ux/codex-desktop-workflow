const toggle = document.getElementById("language-toggle");
const copy = document.getElementById("copy-command");
const command = document.getElementById("install-command");
const demo = document.querySelector(".demo");

function setLanguage(language) {
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-en][data-zh]").forEach((element) => {
    element.textContent = element.dataset[language];
  });
  if (demo) {
    demo.src = language === "zh" ? demo.dataset.zhSrc : demo.dataset.enSrc;
  }
  toggle.textContent = language === "zh" ? "English" : "中文";
  localStorage.setItem("codex-workflow-language", language);
}

toggle.addEventListener("click", () => {
  const next = document.documentElement.lang === "zh-CN" ? "en" : "zh";
  setLanguage(next);
});

copy.addEventListener("click", async () => {
  await navigator.clipboard.writeText(command.textContent.trim());
  const original = copy.textContent;
  copy.textContent = document.documentElement.lang === "zh-CN" ? "已复制" : "Copied";
  setTimeout(() => { copy.textContent = original; }, 1200);
});

setLanguage(localStorage.getItem("codex-workflow-language") || "en");
