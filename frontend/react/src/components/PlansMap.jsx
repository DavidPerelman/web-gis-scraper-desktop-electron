import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const PlansMap = ({ data, hoveredId, setSelectedId, selectedId }) => {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const geoLayerRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current || leafletMap.current) return;

    leafletMap.current = L.map(mapRef.current).setView([32.08, 34.78], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(leafletMap.current);
  }, []);

  useEffect(() => {
    if (!leafletMap.current || !data) return;

    // הסר שכבה קודמת אם קיימת
    if (geoLayerRef.current) {
      geoLayerRef.current.remove();
    }

    geoLayerRef.current = L.geoJSON(data, {
      style: (feature) => ({
        color:
          feature.id === hoveredId || feature.id === selectedId
            ? "#0033cc"
            : "#3388ff",
        weight: feature.id === hoveredId ? 3 : 1,
        fillOpacity: 0.5,
      }),
      onEachFeature: (feature, layer) => {
        const { pl_number, pl_name, station_desc } = feature.properties || {};

        const popupContent = `
          <strong>${pl_number || "ללא מספר"}</strong><br/>
          ${pl_name || "ללא שם"}<br/>
          <em>${station_desc || ""}</em>
        `;
        layer.bindPopup(popupContent);

        layer.on("click", () => {
          if (setSelectedId) {
            setSelectedId(feature.id);
          }
        });
      },
    }).addTo(leafletMap.current);

    // התאמה לתצוגה
    const bounds = geoLayerRef.current.getBounds();
    if (bounds.isValid()) {
      leafletMap.current.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [data, hoveredId, selectedId, setSelectedId]);

  return (
    <div className="w-full max-w-screen-xl mx-auto h-[60vh] rounded-xl overflow-hidden">
      <div ref={mapRef} className="w-full h-full" />
    </div>
  );
};

export default PlansMap;
