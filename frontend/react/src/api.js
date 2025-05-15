// src/api.js

const isFileProtocol = window.location.protocol === "file:";
const API_BASE_URL = isFileProtocol ? "http://127.0.0.1:8000" : "";

/**
 * קריאה ל־API שמתאימה גם ל־Electron וגם ל־Vite
 * @param {string} path - הנתיב היחסי (למשל "/health")
 * @param {object} options - פרמטרים ל־fetch
 * @returns {Promise<Response>}
 */
export async function apiFetch(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  return fetch(url, options);
}
