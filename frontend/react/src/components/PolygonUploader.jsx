import { useState, useEffect, useRef } from "react";
import logo from "../../assets/logo.svg";

const PolygonUploader = ({ onPlansReady, plansGeojson, setPlansGeojson }) => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const abortRef = useRef();
  const fileInputRef = useRef(null);
  // eslint-disable-next-line no-unused-vars
  const [serverResponse, setServerResponse] = useState("");
  const [serverPlans, setServerPlans] = useState(null);
  const [inputKey, setInputKey] = useState(0);

  const handleFileChange = (e) => {
    const uploaded = e.target.files?.[0] || null;
    setFile(uploaded);
  };

  const handleSubmit = async () => {
    if (!file) {
      return;
    }

    setStatus("loading");
    abortRef.current = new AbortController();

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/upload-polygon", {
        method: "POST",
        body: formData,
        signal: abortRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json(); // אם השרת מחזיר JSON
      setServerPlans(data);
      setServerResponse(JSON.stringify(data, null, 2));

      if (onPlansReady) {
        onPlansReady(data); // ← מעביר את רשימת התוכניות ל־App
      }

      setStatus("success");
    } catch (err) {
      setStatus("error");
      if (err instanceof DOMException && err.name === "AbortError") {
        setErrorMessage("ההעלאה בוטלה");
      } else {
        setErrorMessage("אירעה שגיאה במהלך העלאת הקובץ");
      }

      // אפשרות: להחזיר ל־idle אוטומטית אחרי כמה שניות
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  const handleExportDownload = async () => {
    if (!serverPlans) {
      console.error("No plans!");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/export/download", {
        method: "POST",
        body: JSON.stringify(serverPlans),
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get("content-disposition");
      let filename = "plans_export.zip";

      if (contentDisposition && contentDisposition.includes("filename=")) {
        filename = contentDisposition
          .split("filename=")[1]
          .replaceAll('"', "")
          .trim();
      }

      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
      setStatus("success");

      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
    } catch (err) {
      setStatus("error");
      if (err instanceof DOMException && err.name === "AbortError") {
        setErrorMessage("ההעלאה בוטלה");
      } else {
        setErrorMessage("אירעה שגיאה במהלך העלאת הקובץ");
      }

      // אפשרות: להחזיר ל־idle אוטומטית אחרי כמה שניות
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  const handleCancel = () => {
    abortRef.current?.abort();
    setFile(null);
  };

  useEffect(() => {
    return () => {
      if (downloadUrl) {
        URL.revokeObjectURL(downloadUrl);
      }
    };
  }, [downloadUrl]);

  return (
    <div className="max-w-xl mx-auto space-y-6 p-4">
      <div className="space-y-4">
        <div className="flex items-center justify-center gap-3 mb-4">
          <img
            src={logo}
            alt="Logo"
            className="h-10 w-10 object-contain relative -translate-y-[-5px]"
          />
          <h1 className="text-3xl font-bold text-gray-800">GIS Scraper</h1>
        </div>
        <p className="text-gray-600">
          תוכנה לחילוץ נתוני תוכניות בנייה מאתר &quot;מנהל התכנון&quot;. ניתן
          להעלות קובץ פוליגון, ולקבל תוצאה מעובדת: שכבת פוליגונים הכוללת את
          התכניות שבתחום הפוליגון שהועלה, עם נתוני בנייה מורחבים עבור כל תכנית.
        </p>
        <p className="text-gray-600">
          בחר קובץ ← לחץ על &quot;שלח&quot; ← המתן לתשובה ← הורד את הקובץ המעובד
        </p>

        <div className="bg-blue-50 border border-blue-300 text-blue-900 rounded-lg p-4 text-right rtl space-y-2 text-sm">
          <ol className="list-decimal pr-4 space-y-2">
            <li>
              סוג קובץ נתמך: יש להעלות קובץ ZIP המכיל קובץ SHP, שכולל את הקבצים
              הבאים:
              <ul className="list-disc pr-4 mt-1 space-y-1">
                <li>
                  <code>.shp</code> – גיאומטריה
                </li>
                <li>
                  <code>.shx</code> – אינדקס
                </li>
                <li>
                  <code>.dbf</code> – מאפיינים
                </li>
              </ul>
            </li>
            <li>ככל שהפוליגון גדול יותר, כך התהליך עשוי להימשך זמן רב יותר.</li>
          </ol>
        </div>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const droppedFile = e.dataTransfer.files?.[0];
            if (droppedFile) {
              setFile(droppedFile);
            }
          }}
        >
          <label
            htmlFor="file"
            className="block w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition"
          >
            <p className="text-gray-600 mb-2">
              {file ? `✔️ ${file.name}` : "גרור קובץ לכאן או לחץ לבחירה"}
            </p>
            <input
              key={inputKey}
              id="file"
              type="file"
              accept=".zip"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
        </div>

        <div className="text-center">
          {status === "idle" && (
            <button
              className={`px-4 py-2 rounded text-white ${
                file
                  ? "bg-blue-600 hover:bg-blue-700 cursor-pointer"
                  : "bg-gray-300 cursor-not-allowed"
              }`}
              onClick={handleSubmit}
              disabled={!file}
            >
              שלח
            </button>
          )}

          {status === "loading" && (
            <div className="text-center">
              <p className="text-blue-600 mb-2">הבקשה בתהליך...</p>
              <button
                className="px-4 py-2 bg-gray-400 text-white rounded cursor-pointer"
                onClick={handleCancel}
              >
                ביטול
              </button>
            </div>
          )}
        </div>

        {status === "success" && (
          <div className="text-center text-green-600 space-y-2">
            <p>✅ הבקשה הסתיימה בהצלחה</p>
            <button
              onClick={handleExportDownload}
              className="inline-block px-4 py-2 bg-green-600 text-white rounded text-white rounded cursor-pointer"
            >
              הורד כ־Shapefile (ZIP)
            </button>
          </div>
        )}

        {serverPlans && plansGeojson && (
          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setFile(null);
                setStatus("idle");
                setErrorMessage(null);
                setDownloadUrl(null);
                setServerResponse("");
                setServerPlans(null);
                setPlansGeojson(null);
                fileInputRef.current.value = null;
                abortRef.current = null;
                setInputKey((prev) => prev + 1);
                window.scrollTo({ top: 0, behavior: "smooth" }); // גלילה למעלה
              }}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded transition cursor-pointer"
            >
              איפוס והעלאת קובץ חדש
            </button>
          </div>
        )}

        {status === "error" && errorMessage && (
          <p className="text-red-600 text-center">❌ {errorMessage}</p>
        )}
      </div>
    </div>
  );
};

export default PolygonUploader;
