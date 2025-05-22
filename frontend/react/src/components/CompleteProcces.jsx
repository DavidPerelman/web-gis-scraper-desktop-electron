const CompletedProcess = ({
  setInputKey,
  status,
  setStatus,
  plansGeojson,
  setPlansGeojson,
  handleExportDownload,
  setErrorMessage,
  setDownloadUrl,
  setFile,
  abortRef,
  setServerPlans,
  setServerResponse,
  setPolygonGeoJSON,
}) => {
  return (
    <div>
      <div className="text-center"></div>
      {status === "success" && (
        <div className="text-center text-green-600 space-y-2">
          <p>✅ הבקשה הסתיימה בהצלחה</p>

          {plansGeojson && plansGeojson.features.length > 0 ? (
            <button
              onClick={handleExportDownload}
              className="inline-block px-4 py-2 bg-green-600 text-white rounded text-white rounded cursor-pointer mt-2"
            >
              הורד כ־Shapefile (ZIP)
            </button>
          ) : (
            <p className="text-yellow-600 text-center">
              ⚠️ לא נמצאו תוכניות בתחום שבחרת
            </p>
          )}
        </div>
      )}
      {status === "success" && (
        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setFile(null);
              setPolygonGeoJSON(null);
              setStatus("idle");
              setErrorMessage(null);
              setDownloadUrl(null);
              setServerResponse("");
              setServerPlans(null);
              setPlansGeojson(null);
              abortRef.current = null;
              setInputKey((prev) => prev + 1);
              window.scrollTo({ top: 0, behavior: "smooth" }); // גלילה למעלה
            }}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded transition cursor-pointer mb-5"
          >
            איפוס והעלאת קובץ חדש
          </button>
        </div>
      )}
    </div>
  );
};

export default CompletedProcess;
