const ActionContainer = ({
  file,
  setFile,
  abortRef,
  setInputKey,
  status,
  setStatus,
  setErrorMessage,
  handlePlansReady,
  setServerPlans,
  setServerResponse,
  polygonGeoJSON,
  setPolygonGeoJSON,
  fileInputRef,
}) => {
  const handleSubmit = async () => {
    setStatus("loading");

    if (file) {
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
        handlePlansReady(data);
      } catch (err) {
        setStatus("error");
        if (err instanceof DOMException && err.name === "AbortError") {
          setErrorMessage("ההעלאה בוטלה");
        } else {
          setStatus("error");
          setErrorMessage("שגיאה בשליחה לשרת");
        }

        // אפשרות: להחזיר ל־idle אוטומטית אחרי כמה שניות
        setTimeout(() => setStatus("idle"), 3000);
      }
    } else if (polygonGeoJSON) {
      handleFetchPlans();
    } else {
      return;
    }
  };

  const handleCancel = () => {
    setStatus("idle");
    abortRef.current?.abort();

    setFile(null);
    setPolygonGeoJSON(null);
    setInputKey((prev) => prev + 1);

    if (fileInputRef.current) {
      fileInputRef.current.value = ""; // איפוס שדה העלאת הקובץ
    }
  };

  const handleFetchPlans = async () => {
    if (!polygonGeoJSON) return;

    setStatus("loading");
    abortRef.current = new AbortController();

    try {
      const response = await fetch("http://localhost:8000/plans/by-polygon", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(polygonGeoJSON),
        signal: abortRef.current.signal,
      });

      if (!response.ok) throw new Error("שגיאה מהשרת");

      const data = await response.json();

      setServerPlans(data);
      setServerResponse(JSON.stringify(data, null, 2));
      handlePlansReady(data);
    } catch (err) {
      setStatus("error");
      if (err instanceof DOMException && err.name === "AbortError") {
        setErrorMessage("ההעלאה בוטלה");

        // אפשרות: להחזיר ל־idle אוטומטית אחרי כמה שניות
        setTimeout(() => setStatus("idle"), 3000);
      } else {
        setStatus("error");
        setErrorMessage("שגיאה בשליחה לשרת");
        setTimeout(() => setStatus("idle"), 3000);
      }
    }
  };

  return (
    <div>
      <div className="text-center">
        {status === "idle" && (
          <button
            className={`px-4 py-2 rounded text-white mt-5 ${
              file || polygonGeoJSON
                ? "bg-blue-600 hover:bg-blue-700 cursor-pointer"
                : "bg-gray-300 cursor-not-allowed"
            }`}
            onClick={handleSubmit}
            disabled={!(!!file || !!polygonGeoJSON)}
          >
            שלח
          </button>
        )}

        {status === "loading" && (
          <div className="text-center">
            <p className="text-blue-600 mb-5">הבקשה בתהליך...</p>
            <button
              className="px-4 py-2 bg-gray-400 text-white rounded cursor-pointer"
              onClick={handleCancel}
            >
              ביטול
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ActionContainer;
