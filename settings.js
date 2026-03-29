const DEFAULT_SETTINGS = {
  questionCount: 10,
  displayMode: "grid",
  masteryThreshold: 3,
  includeMastered: false,
  prioritizeWrong: true,
};

function loadSettings() {
  try {
    const saved = JSON.parse(localStorage.getItem("torioboe_settings"));
    return { ...DEFAULT_SETTINGS, ...saved };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

function saveSettings(settings) {
  localStorage.setItem("torioboe_settings", JSON.stringify(settings));
}
