import { useState } from "react";
import "./App.css";
import PlansMap from "./components/PlansMap";
import PlansTable from "./components/PlansTable";
import PolygonUploader from "./components/PolygonUploader";

function App() {
  const [plansGeojson, setPlansGeojson] = useState(null);
  const [hoveredPlanId, setHoveredPlanId] = useState(null);
  const [selectedPlanId, setSelectedPlanId] = useState(null);

  const handlePlansReady = async (plans) => {
    fetch("http://localhost:8000/export/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(plans), // נוודא שפה יש את הנתונים הנכונים
    })
      .then((res) => res.json())
      .then((geojson) => {
        if (!geojson.features || geojson.features.length === 0) {
          console.error("❌ No valid features in the GeoJSON!");
          return;
        }
        setPlansGeojson(geojson);
      })
      .catch((err) => console.error("❌ Error fetching GeoJSON:", err));
  };

  return (
    <>
      <PolygonUploader onPlansReady={handlePlansReady} />
      {plansGeojson && (
        <>
          <PlansMap
            data={plansGeojson}
            hoveredId={hoveredPlanId}
            setSelectedId={setSelectedPlanId}
          />
          <PlansTable
            data={plansGeojson}
            setHoveredId={setHoveredPlanId}
            selectedId={selectedPlanId}
          />
        </>
      )}
    </>
  );
}

export default App;
