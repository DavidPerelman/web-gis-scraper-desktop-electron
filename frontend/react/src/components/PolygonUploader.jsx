import { useEffect } from "react";
import logo from "../../assets/logo.svg";

window.type = window.type || "";

const PolygonUploader = ({
  fileInputRef,
  file,
  setFile,
  inputKey,
  downloadUrl,
}) => {
  useEffect(() => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, [inputKey, fileInputRef]);

  const handleFileChange = (e) => {
    const uploaded = e.target.files?.[0] || null;
    setFile(uploaded);
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
      </div>
    </div>
  );
};

export default PolygonUploader;
