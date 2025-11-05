import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import axios from "axios";

export default function ComplianceTrends() {
  const [data, setData] = useState([]);
  const [days, setDays] = useState(30);

  useEffect(() => {
    axios.get(`/api/compliance/trends?days=${days}`)
      .then((res) => setData(res.data))
      .catch((err) => console.error("Trend fetch failed:", err));
  }, [days]);

  return (
    <div className="bg-white rounded-xl p-4 shadow">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-semibold">Compliance Trends (Last {days} Days)</h2>
        <select value={days} onChange={(e) => setDays(e.target.value)} className="border rounded px-2 py-1">
          <option value={7}>7 Days</option>
          <option value={30}>30 Days</option>
          <option value={90}>90 Days</option>
        </select>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="pass" fill="#22c55e" name="Pass" />
          <Bar dataKey="fail" fill="#ef4444" name="Fail" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
