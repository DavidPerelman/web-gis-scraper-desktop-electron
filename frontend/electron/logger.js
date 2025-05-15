const fs = require("fs");
const path = require("path");

const logPath = path.join(__dirname, "log.txt");

function logToFile(...args) {
  const message = args.map(String).join(" ") + "\n";
  fs.appendFileSync(logPath, `[${new Date().toISOString()}] ${message}`);
  console.log(...args);
}

module.exports = { logToFile };
