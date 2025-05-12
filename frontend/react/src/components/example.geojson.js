// example.geojson.js
export const exampleGeojson = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        pl_number: "101-000001",
        pl_name: "תכנית מגורים לדוגמה",
        station_desc: "אישור",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [34.7801, 32.0853],
            [34.7815, 32.0853],
            [34.7815, 32.0865],
            [34.7801, 32.0865],
            [34.7801, 32.0853],
          ],
        ],
      },
    },
  ],
};
