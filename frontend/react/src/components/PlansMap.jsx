import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect } from "react";

const FitBounds = ({ data }) => {
  const map = useMap();

  useEffect(() => {
    const geoJsonLayer = L.geoJSON(data);
    const bounds = geoJsonLayer.getBounds();
    if (bounds.isValid()) {
      map.fitBounds(bounds);
    }
  }, [data, map]);

  return null;
};

const onEachFeature = (feature, layer) => {
  const { pl_number, pl_name, station_desc } = feature.properties || {};
  const popupContent = `
    <strong>${pl_number || "ללא מספר"}</strong><br/>
    ${pl_name || "ללא שם"}<br/>
    <em>${station_desc || ""}</em>
  `;
  layer.bindPopup(popupContent);
};

const PlansMap = ({ data, hoveredId }) => {
  return (
    <div className="w-full max-w-screen-xl mx-auto h-[500px] rounded-xl overflow-hidden">
      <MapContainer
        center={[32.08, 34.78]}
        zoom={12}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON
          data={data}
          style={(feature) => ({
            color: feature.id === hoveredId ? "#0033cc" : "#3388ff",
            weight: feature.id === hoveredId ? 3 : 1,
            fillOpacity: 0.5,
          })}
          onEachFeature={onEachFeature}
        />
        <FitBounds data={data} />
      </MapContainer>
    </div>
  );
};

export default PlansMap;
