// frontend/src/services/mockAlertSettings.js

// Simulated delay
const delay = (ms) => new Promise((res) => setTimeout(res, ms));

// Default settings (simulate backend load)
let mockSettings = {
  scan_failed: true,
  compliance_violation: true,
  agent_offline: false,
  threshold_breach: false,
};

export async function getMockAlertSettings() {
  await delay(300); // simulate network delay
  return { ...mockSettings }; // return a copy
}

export async function saveMockAlertSettings(newSettings) {
  await delay(500); // simulate save time
  try {
    mockSettings = { ...newSettings }; // overwrite
    return true;
  } catch {
    return false;
  }
}