const { app, BrowserWindow, ipcMain, screen } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const http = require("http");

function logToFile(...args) {
  try {
    const logDir = app.getPath("userData");
    const logPath = path.join(logDir, "log.txt");

    const message = args
      .map((a) => (typeof a === "string" ? a : JSON.stringify(a)))
      .join(" ");
    const full = `[${new Date().toISOString()}] ${message}\n`;

    fs.appendFileSync(logPath, full);
  } catch (err) {
    console.error("Failed to write log:", err.message);
  }
}

const isDev =
  !app.isPackaged ||
  process.env.ELECTRON_IS_DEV === "1" ||
  process.defaultApp ||
  /node_modules[\\/]electron[\\/]/.test(process.execPath);

// הדפסת סטטוס
logToFile("App launched");
logToFile("app.isPackaged =", app.isPackaged);
logToFile("isDev =", isDev);
logToFile("process.execPath =", process.execPath);
logToFile("__dirname =", __dirname);

let mainWindow = null;
let serverProcess = null;

function startServerProcess() {
  const exePath = isDev
    ? path.join(__dirname, "extra", "run_server", "run_server.exe")
    : path.join(process.resourcesPath, "extra", "run_server", "run_server.exe");

  logToFile("Executing server from:", exePath);

  if (!fs.existsSync(exePath)) {
    logToFile("run_server.exe not found at", exePath);
    return;
  }

  serverProcess = spawn(exePath, {
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });

  serverProcess.stdout.on("data", (data) => {
    logToFile("[FastAPI STDOUT]", data.toString());
  });

  serverProcess.stderr.on("data", (data) => {
    logToFile("[FastAPI STDERR]", data.toString());
  });

  serverProcess.on("exit", (code, signal) => {
    logToFile(`Server process exited with code=${code}, signal=${signal}`);
  });
}

function waitForServerReady(timeout = 15000, interval = 500) {
  const deadline = Date.now() + timeout;

  return new Promise((resolve, reject) => {
    function ping() {
      http
        .get("http://127.0.0.1:8000/health", (res) => {
          res.statusCode === 200 ? resolve() : retry();
        })
        .on("error", retry);
    }

    function retry() {
      if (Date.now() > deadline) reject(new Error("Server not ready in time"));
      else setTimeout(ping, interval);
    }

    ping();
  });
}

async function createWindow() {
  startServerProcess();
  logToFile("Server process started");

  try {
    await waitForServerReady();
    logToFile("Server is ready");
  } catch (e) {
    logToFile("Server failed to start:", e.toString());
    const failWin = new BrowserWindow({ width: 500, height: 300 });
    failWin.loadURL(
      "data:text/html,<h1>Server Failed</h1><p>See log.txt for details</p>"
    );
    return;
  }

  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  const win = new BrowserWindow({
    width: Math.floor(width * 0.8),
    height: Math.floor(height * 0.8),
    icon: path.join(__dirname, "assets", "logo.png"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
    },
  });

  if (isDev) {
    win.loadURL("http://localhost:5173");
  } else {
    const indexPath = path.join(__dirname, "..", "react", "dist", "index.html");
    logToFile("Loading UI from:", indexPath);
    win.loadFile(indexPath);
  }

  win.on("closed", () => (mainWindow = null));
  mainWindow = win;
}

ipcMain.handle("ping", () => {
  return "pong from main process";
});

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (serverProcess) {
    logToFile("Killing server process...");
    serverProcess.kill();
  }
  if (process.platform !== "darwin") app.quit();
});
