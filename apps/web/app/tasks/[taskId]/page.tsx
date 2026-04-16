"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { getTask, runTask, TaskDetail } from "../../../lib/api";

export default function TaskDetailPage() {
  const params = useParams<{ taskId: string }>();
  const taskId = useMemo(() => {
    const raw = params?.taskId;
    return Array.isArray(raw) ? raw[0] : raw;
  }, [params]);

  const [task, setTask] = useState<TaskDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    if (!taskId) return;
    const data = await getTask(taskId);
    setTask(data);
  }

  useEffect(() => {
    if (!taskId) return;

    setLoading(true);
    getTask(taskId)
      .then(setTask)
      .catch((err) => setError(err.message || "Failed to load task"))
      .finally(() => setLoading(false));
  }, [taskId]);

  useEffect(() => {
    if (!task) return;
    if (task.status !== "pending" && task.status !== "running") return;

    const timer = setInterval(() => {
      refresh().catch(() => {});
    }, 2000);

    return () => clearInterval(timer);
  }, [task]);

  async function handleRun() {
    if (!taskId) return;
    setError("");
    try {
      setRunning(true);
      await runTask(taskId);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run task");
    } finally {
      setRunning(false);
    }
  }

  return (
    <main>
      <h1>Task Detail</h1>

      {loading && <p>Loading task...</p>}
      {error && (
        <div
          style={{
            background: "#ffe5e5",
            color: "#8b0000",
            padding: 12,
            borderRadius: 10,
            marginBottom: 16
          }}
        >
          {error}
        </div>
      )}

      {task && (
        <div
          style={{
            display: "grid",
            gap: 16
          }}
        >
          <div
            style={{
              background: "#fff",
              padding: 20,
              borderRadius: 12,
              boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
            }}
          >
            <div><strong>ID:</strong> {task.id}</div>
            <div><strong>Status:</strong> {task.status}</div>
            <div><strong>Uploaded File ID:</strong> {task.uploaded_file_id}</div>
            <div><strong>Template ID:</strong> {task.template_id}</div>
            <div><strong>Delimiter:</strong> {task.delimiter}</div>
            <div><strong>Has Header:</strong> {String(task.has_header)}</div>
            {task.error_message && (
              <div style={{ marginTop: 12, color: "crimson" }}>
                <strong>Error:</strong> {task.error_message}
              </div>
            )}

            {(task.status === "pending" || task.status === "running") && (
              <button
                onClick={handleRun}
                disabled={running || task.status === "running"}
                style={{
                  marginTop: 16,
                  padding: "10px 14px",
                  borderRadius: 8,
                  border: "none",
                  background: "#111827",
                  color: "#fff",
                  cursor: "pointer"
                }}
              >
                {task.status === "running" ? "Running..." : running ? "Running..." : "Run Task"}
              </button>
            )}
          </div>

          {task.artifacts && Object.keys(task.artifacts).length > 0 && (
            <div
              style={{
                background: "#fff",
                padding: 20,
                borderRadius: 12,
                boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
              }}
            >
              <h2>Artifacts</h2>
              <ul>
                {Object.entries(task.artifacts).map(([key, value]) => (
                  <li key={key}>
                    <strong>{key}:</strong>{" "}
                    <a href={value} target="_blank" rel="noreferrer">
                      Open
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {task.artifacts?.report && (
            <div
              style={{
                background: "#fff",
                padding: 20,
                borderRadius: 12,
                boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
              }}
            >
              <h2>Report Preview</h2>
              <iframe
                src={task.artifacts.report}
                style={{
                  width: "100%",
                  height: 500,
                  border: "1px solid #ddd",
                  borderRadius: 8
                }}
              />
            </div>
          )}
        </div>
      )}
    </main>
  );
}
