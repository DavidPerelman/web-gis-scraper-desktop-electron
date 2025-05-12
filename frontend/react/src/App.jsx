import "./App.css";
import PlansMap from "./components/PlansMap";
import PolygonUploader from "./components/PolygonUploader";
import { exampleGeojson } from "./components/example.geojson";

function App() {
  return (
    <>
      {/* <PolygonUploader key="upload" /> */}
      <h1 className="text-xl font-bold mb-4">תצוגת תכניות לדוגמה</h1>
      <PlansMap data={exampleGeojson} />
    </>
  );
}

export default App;
