const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let fastapiProcess;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
    },
  });

  // טען את build של React מתוך dist/
  const indexPath = path.join(__dirname, "../react/dist/index.html");
  win.loadFile(indexPath);
}

function startFastAPI() {
  // 🔧 עדכן כאן את הנתיב המדויק של uvicorn.exe מתוך .venv
  const scriptPath =
    "C:/Users/dpere/Documents/python-projects/web-gis-scraper-desktop-electron/.venv/Scripts/uvicorn.exe";
  const appPath = path.join(__dirname, "../../backend/main.py");

  fastapiProcess = spawn(
    `"${scriptPath}"`,
    [appPath, "--host", "127.0.0.1", "--port", "8000"],
    {
      shell: true,
      detached: false,
    }
  );

  fastapiProcess.stdout.on("data", (data) => {
    console.log(`[FastAPI]: ${data}`);
  });

  fastapiProcess.stderr.on("data", (data) => {
    console.error(`[FastAPI ERROR]: ${data}`);
  });
}

app.whenReady().then(() => {
  startFastAPI();
  createWindow();
});

app.on("window-all-closed", () => {
  if (fastapiProcess) {
    fastapiProcess.kill();
  }
  if (process.platform !== "darwin") {
    app.quit();
  }
});
