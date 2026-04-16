"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getSystemCheck } from "../../lib/api";

export default function SystemPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getSystemCheck()
      .then(setData)
      .catch((err) => setError(err.message || "Failed to load system check"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <h1>System Check</h1>
      <p>
        <Link href="/">Back Home</Link>
      </p>

      {loading && <p>Loading system check...</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {data && (
        <pre
          style={{
            background: "#fff",
            padding: 20,
            borderRadius: 12,
            boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
            overflow: "auto"
          }}
        >
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </main>
  );
}
