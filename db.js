const DB_NAME = "torioboe";
const DB_VERSION = 1;
const STORE_NAME = "progress";

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };

    request.onsuccess = (event) => {
      resolve(event.target.result);
    };

    request.onerror = (event) => {
      reject(event.target.error);
    };
  });
}

function getProgress(id) {
  return openDB().then((db) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readonly");
      const store = tx.objectStore(STORE_NAME);
      const request = store.get(id);

      request.onsuccess = (event) => {
        resolve(event.target.result || null);
      };

      request.onerror = (event) => {
        reject(event.target.error);
      };
    });
  });
}

function saveProgress(record) {
  return openDB().then((db) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      const store = tx.objectStore(STORE_NAME);
      const request = store.put(record);

      request.onsuccess = () => {
        resolve();
      };

      request.onerror = (event) => {
        reject(event.target.error);
      };
    });
  });
}

function getAllProgress() {
  return openDB().then((db) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readonly");
      const store = tx.objectStore(STORE_NAME);
      const request = store.getAll();

      request.onsuccess = (event) => {
        resolve(event.target.result);
      };

      request.onerror = (event) => {
        reject(event.target.error);
      };
    });
  });
}

function clearAllProgress() {
  return openDB().then((db) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      const store = tx.objectStore(STORE_NAME);
      const request = store.clear();

      request.onsuccess = () => {
        resolve();
      };

      request.onerror = (event) => {
        reject(event.target.error);
      };
    });
  });
}

function exportData() {
  return getAllProgress().then((progress) => {
    const settings = loadSettings();
    return JSON.stringify({ progress, settings });
  });
}

function normalizeImportedRecord(record) {
  if (!record || typeof record !== "object" || Array.isArray(record)) {
    throw new Error("Invalid progress record");
  }

  if (typeof record.id !== "string" || record.id.trim() === "") {
    throw new Error("Progress record is missing a valid id");
  }

  return {
    id: record.id,
    correctStreak: Number(record.correctStreak) || 0,
    totalAttempts: Number(record.totalAttempts) || 0,
    correctTotal: Number(record.correctTotal ?? record.totalCorrect) || 0,
    mastered: Boolean(record.mastered),
    lastSeen: typeof record.lastSeen === "string" ? record.lastSeen : null,
  };
}

function importData(jsonString) {
  let data;
  try {
    data = JSON.parse(jsonString);
  } catch (e) {
    return Promise.reject(new Error("Invalid JSON"));
  }

  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return Promise.reject(new Error("Invalid import format"));
  }

  const rawProgressRecords = data.progress ?? [];
  if (!Array.isArray(rawProgressRecords)) {
    return Promise.reject(new Error("Progress data must be an array"));
  }

  const progressRecords = rawProgressRecords.map(normalizeImportedRecord);
  const settings =
    data.settings && typeof data.settings === "object" && !Array.isArray(data.settings)
      ? data.settings
      : {};

  return openDB().then((db) => {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      const store = tx.objectStore(STORE_NAME);

      store.clear();
      progressRecords.forEach((record) => {
        store.put(record);
      });

      tx.oncomplete = () => {
        saveSettings({ ...DEFAULT_SETTINGS, ...settings });
        resolve();
      };

      tx.onerror = (event) => {
        reject(event.target.error);
      };

      tx.onabort = (event) => {
        reject(event.target.error || tx.error || new Error("Import transaction aborted"));
      };
    });
  });
}
