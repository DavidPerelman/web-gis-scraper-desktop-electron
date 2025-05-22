"use client";

import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-draw"; // חובה!

const PolygonDrawer = ({
  status,
  // handleExportDownload,
  setPolygonGeoJSON,
  polygonGeoJSON,
  clearPolygon,
}) => {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const drawnItems = useRef(null);
  const [mapReady, setMapReady] = useState(false); // ✅ חדש

  useEffect(() => {
    if (clearPolygon && drawnItems.current) {
      drawnItems.current.clearLayers();
    }
  }, [clearPolygon]);

  // 🧭 יצירת מפה – רץ פעם אחת בלבד
  useEffect(() => {
    if (!mapRef.current || leafletMap.current) return;

    leafletMap.current = L.map(mapRef.current).setView([32, 35], 10);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(leafletMap.current);

    drawnItems.current = new L.FeatureGroup();
    leafletMap.current.addLayer(drawnItems.current);

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

    leafletMap.current.on(L.Draw.Event.CREATED, (event) => {
      drawnItems.current.clearLayers();
      const layer = event.layer;
      drawnItems.current.addLayer(layer);

      const geojson = layer.toGeoJSON();
      setPolygonGeoJSON(geojson);
      console.log("check");
      console.log(status);
    });

    setMapReady(true); // ✅ סימון מוכנות
  }, [setPolygonGeoJSON]);

  // 📦 רינדור polygonGeoJSON מבחוץ (למשל אחרי שגיאה)
  useEffect(() => {
    if (
      !mapReady ||
      !polygonGeoJSON ||
      !polygonGeoJSON.geometry ||
      !Array.isArray(polygonGeoJSON.geometry.coordinates)
    ) {
      return;
    }

    const layerGroup = drawnItems.current;
    if (!layerGroup) {
      console.warn("⚠️ drawnItems לא מאותחל עדיין");
      return;
    }

    try {
      layerGroup.clearLayers();
      const geoJsonLayer = L.geoJSON(polygonGeoJSON);
      const layers = geoJsonLayer.getLayers();
      if (layers.length > 0) {
        layerGroup.addLayer(layers[0]);
      }
    } catch (err) {
      console.error("❌ שגיאה בהצגת polygonGeoJSON:", err);
    }
  }, [polygonGeoJSON, mapReady]);

  return (
    <div className="space-y-4">
      <div ref={mapRef} style={{ height: "500px", width: "100%" }} />
    </div>
  );
};

export default PolygonDrawer;
