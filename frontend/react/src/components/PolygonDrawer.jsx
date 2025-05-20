"use client";

import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-draw"; // חשוב לייבא!

const PolygonDrawer = ({ onFetchPlans }) => {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const drawnItems = useRef(null);
  const [polygonGeoJSON, setPolygonGeoJSON] = useState(null);

  useEffect(() => {
    if (!mapRef.current || leafletMap.current) return;

    // יצירת מפה
    leafletMap.current = L.map(mapRef.current).setView([32, 35], 10);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(leafletMap.current);

    // שכבת ציור
    drawnItems.current = new L.FeatureGroup();
    leafletMap.current.addLayer(drawnItems.current);

    // כפתורי ציור
    const drawControl = new L.Control.Draw({
      draw: {
        polygon: {
          allowIntersection: false,
          showArea: true,
        },
        polyline: false,
        rectangle: false,
        circle: false,
        marker: false,
        circlemarker: false,
      },
      edit: {
        featureGroup: drawnItems.current,
        remove: true,
      },
    });

    leafletMap.current.addControl(drawControl);

    // אירוע יצירת פוליגון
    leafletMap.current.on(L.Draw.Event.CREATED, (event) => {
      drawnItems.current.clearLayers(); // רק אחד
      const layer = event.layer;
      drawnItems.current.addLayer(layer);

      const geojson = layer.toGeoJSON();
      setPolygonGeoJSON(geojson);
      console.log("🎯 Polygon drawn:", geojson);
    });
  }, []);

  // שליחה לשרת
  const handleFetchPlans = async () => {
    if (!polygonGeoJSON) return;

    try {
      const response = await fetch("http://localhost:8000/plans/by-polygon", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(polygonGeoJSON),
      });

      if (!response.ok) throw new Error("שגיאה מהשרת");

      const result = await response.json();
      console.log("📦 תוכניות מהשרת:", result);
      onFetchPlans(result); // העבר לקומפוננטת האב
    } catch (err) {
      console.error("❌ שגיאה:", err);
      alert("שגיאה בשליחה לשרת");
    }
  };

  return (
    <div className="space-y-4">
      <div ref={mapRef} style={{ height: "500px", width: "100%" }} />
      {polygonGeoJSON && (
        <button
          onClick={handleFetchPlans}
          className="px-4 py-2 bg-blue-600 text-white rounded cursor-pointer"
        >
          שלוף תוכניות
        </button>
      )}
    </div>
  );
};

export default PolygonDrawer;
