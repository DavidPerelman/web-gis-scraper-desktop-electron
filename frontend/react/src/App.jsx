import { useState, useRef } from "react";
import "./App.css";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import PlansMap from "./components/PlansMap";
import PlansTable from "./components/PlansTable";
import PolygonUploader from "./components/PolygonUploader";
import PolygonDrawer from "./components/PolygonDrawer";
import CompletedProcess from "./components/CompleteProcces";
import ActionContainer from "./components/ActionContainer";

function App() {
  const [plansGeojson, setPlansGeojson] = useState(null);
  const [hoveredPlanId, setHoveredPlanId] = useState(null);
  const [selectedPlanId, setSelectedPlanId] = useState(null);
  const [serverPlans, setServerPlans] = useState(null);
  const [file, setFile] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [serverResponse, setServerResponse] = useState("");
  const [status, setStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [inputKey, setInputKey] = useState(0);
  const abortRef = useRef();
  const [polygonGeoJSON, setPolygonGeoJSON] = useState(null);
  const fileInputRef = useRef(null);

  const handlePlansReady = async (plans) => {
    fetch("http://localhost:8000/export/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(plans), // נוודא שפה יש את הנתונים הנכונים
    })
      .then((res) => res.json())
      .then((geojson) => {
        if (!geojson.features || geojson.features.length === 0) {
          console.error("No valid features in the GeoJSON!");
          return;
        }
        setPlansGeojson(geojson);
        setPolygonGeoJSON(null);
        setStatus("success");
      })
      .catch((err) => console.error("Error fetching GeoJSON:", err));
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

  return (
    <>
      <PolygonUploader
        fileInputRef={fileInputRef}
        file={file}
        setFile={setFile}
        inputKey={inputKey}
        downloadUrl={downloadUrl}
      />

      {status !== "loading" && status !== "success" && (
        <PolygonDrawer
          status={status}
          setStatus={setStatus}
          handleExportDownload={handleExportDownload}
          setPolygonGeoJSON={setPolygonGeoJSON}
          polygonGeoJSON={polygonGeoJSON}
          clearPolygon={status === "success"}
        />
      )}
      <ActionContainer
        file={file}
        setFile={setFile}
        abortRef={abortRef}
        setInputKey={setInputKey}
        status={status}
        setStatus={setStatus}
        errorMessage={errorMessage}
        setErrorMessage={setErrorMessage}
        handlePlansReady={handlePlansReady}
        setServerPlans={setServerPlans}
        setServerResponse={setServerResponse}
        polygonGeoJSON={polygonGeoJSON}
        setPolygonGeoJSON={setPolygonGeoJSON}
        fileInputRef={fileInputRef}
      />
      <CompletedProcess
        setFile={setFile}
        setInputKey={setInputKey}
        abortRef={abortRef}
        status={status}
        setStatus={setStatus}
        setErrorMessage={setErrorMessage}
        setDownloadUrl={setDownloadUrl}
        errorMessage={errorMessage}
        serverPlans={serverPlans}
        setServerPlans={setServerPlans}
        setServerResponse={setServerResponse}
        setPolygonGeoJSON={setPolygonGeoJSON}
        handleExportDownload={handleExportDownload}
        plansGeojson={plansGeojson}
        setPlansGeojson={setPlansGeojson}
      />
      {status === "error" && errorMessage && (
        <p className="text-red-600 text-center mt-5">❌ {errorMessage}</p>
      )}
      {plansGeojson && status === "success" && (
        <>
          <PlansMap
            data={plansGeojson}
            hoveredId={hoveredPlanId}
            selectedId={selectedPlanId}
            setSelectedId={setSelectedPlanId}
          />
          <PlansTable
            data={plansGeojson}
            setHoveredId={setHoveredPlanId}
            selectedId={selectedPlanId}
            setSelectedId={setSelectedPlanId}
          />
        </>
      )}
    </>
  );
}

export default App;
