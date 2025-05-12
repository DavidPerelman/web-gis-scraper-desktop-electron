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

const PlansTable = ({ data, setHoveredId }) => {
  const headers = {
    ...generalFields,
    ...labelToKey,
  };

  return (
    <div className="w-full overflow-x-auto mt-6">
      <div className="min-w-[1000px] mx-auto">
        <table className="w-full border border-gray-300 text-sm text-right rtl">
          <thead className="bg-gray-200">
            <tr>
              {Object.keys(headers).map((label) => (
                <th
                  key={label}
                  className="p-2 border whitespace-nowrap text-sm text-right"
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
                onMouseEnter={() => setHoveredId(feature.id)}
                onMouseLeave={() => setHoveredId(null)}
                className="border-t cursor-pointer"
              >
                {Object.values(headers).map((key) => (
                  <td key={key} className="p-2 border text-center">
                    {key === "pl_url" && feature.properties[key] ? (
                      <a
                        href={feature.properties[key]}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 underline"
                      >
                        לינק
                      </a>
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
