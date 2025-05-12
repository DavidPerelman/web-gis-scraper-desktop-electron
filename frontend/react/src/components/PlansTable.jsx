const labelToKey = {
  'סה"כ שטח בדונם': "area_dunam",
  'מגורים (יח"ד)': "res_units",
  'מגורים (מ"ר)': "res_sqm",
  'מסחר (מ"ר)': "com_sqm",
  'תעסוקה (מ"ר)': "emp_sqm",
  'מבני ציבור (מ"ר)': "pub_sqm",
  "חדרי מלון / תיירות (חדר)": "h_rooms",
  'חדרי מלון / תיירות (מ"ר)': "hotel_sqm",
  'דירות קטנות (יח"ד)': "small_res",
  "תחבורה - רק\"ל (מס' תחנות)": "lrt_station_count", // אם קיים
  'תחבורה - רק"ל (ק"מ)': "lrt_km", // אם קיים
};

const generalFields = {
  "מספר תכנית": "pl_number",
  שם: "pl_name",
  סטטוס: "status",
  עיר: "district",
  "קישור לתכנית": "pl_url",
};

const PlansTable = ({ data, setHoveredId, selectedId, setSelectedId }) => {
  const headers = {
    ...generalFields,
    ...labelToKey,
  };

  return (
    <div className="w-full max-w-screen-xl mx-auto mt-6">
      <div className="overflow-y-auto max-h-[45vh] border border-gray-300 rounded">
        <table className="min-w-max w-full text-sm text-right rtl">
          <thead className="bg-gray-200">
            <tr>
              {Object.keys(headers).map((label) => (
                <th
                  key={label}
                  className="p-2 border whitespace-nowrap text-sm text-right p-1 border text-xs whitespace-nowrap text-right"
                >
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.features.map((feature, idx) => (
              <tr
                key={idx}
                onClick={() => setSelectedId?.(feature.id)}
                onMouseEnter={() => setHoveredId(feature.id)}
                onMouseLeave={() => setHoveredId(null)}
                className={`border-t cursor-pointer ${
                  feature.id === selectedId ? "bg-blue-100 font-bold" : ""
                }`}
              >
                {Object.values(headers).map((key) => (
                  <td
                    key={key}
                    className={`p-1 border text-center text-xs ${
                      key === "pl_name"
                        ? "whitespace-nowrap max-w-[200px] overflow-hidden text-ellipsis"
                        : ""
                    }`}
                  >
                    {key === "pl_url" && feature.properties[key] ? (
                      <a
                        href={feature.properties[key]}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 underline"
                      >
                        לינק
                      </a>
                    ) : key === "pl_name" ? (
                      (feature.properties[key]?.slice(0, 40) || "") +
                      (feature.properties[key]?.length > 40 ? "..." : "")
                    ) : (
                      feature.properties[key] ?? ""
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PlansTable;
