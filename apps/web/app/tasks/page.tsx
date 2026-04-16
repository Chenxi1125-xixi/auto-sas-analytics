"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getTasks, TaskListItem } from "../../lib/api";

export default function TasksPage() {
  const [tasks, setTasks] = useState<TaskListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getTasks()
      .then(setTasks)
      .catch((err) => setError(err.message || "Failed to load tasks"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Tasks</h1>
        <Link href="/tasks/new">New Task</Link>
      </div>

      {loading && <p>Loading tasks...</p>}
      {error && <p style={{ color: "crimson" }}>{error}</p>}

      {!loading && !error && tasks.length === 0 && (
        <div
          style={{
            background: "#fff",
            padding: 16,
            borderRadius: 12,
            marginTop: 12
          }}
        >
          No tasks yet.
        </div>
      )}

      {!loading && !error && tasks.length > 0 && (
        <div style={{ display: "grid", gap: 12, marginTop: 16 }}>
          {tasks.map((task) => (
            <Link
              key={task.id}
              href={`/tasks/${task.id}`}
              style={{
                textDecoration: "none",
                color: "inherit",
                background: "#fff",
                padding: 16,
                borderRadius: 12,
                boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
              }}
            >
              <div><strong>ID:</strong> {task.id}</div>
              <div><strong>Status:</strong> {task.status}</div>
              <div><strong>Created:</strong> {task.created_at}</div>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
