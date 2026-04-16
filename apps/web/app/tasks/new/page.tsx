"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createTask, getTemplates, Template, uploadFile } from "../../../lib/api";

export default function NewTaskPage() {
  const router = useRouter();

  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [delimiter, setDelimiter] = useState<"comma" | "tab" | "space">("comma");
  const [hasHeader, setHasHeader] = useState(true);
  const [file, setFile] = useState<File | null>(null);

  const [loadingTemplates, setLoadingTemplates] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getTemplates()
      .then((data) => {
        setTemplates(data);
        if (data.length > 0) setSelectedTemplate(data[0].slug);
      })
      .catch((err) => setError(err.message || "Failed to load templates"))
      .finally(() => setLoadingTemplates(false));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!file) {
      setError("Please choose a CSV or TXT file.");
      return;
    }

    if (!selectedTemplate) {
      setError("Please choose a template.");
      return;
    }

    try {
      setSubmitting(true);
      const uploaded = await uploadFile(file);
      const task = await createTask({
        uploaded_file_id: uploaded.id,
        template_slug: selectedTemplate,
        delimiter,
        has_header: hasHeader,
        params_json: {}
      });
      router.push(`/tasks/${task.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <h1>New Task</h1>

      {loadingTemplates && <p>Loading templates...</p>}
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

      <form
        onSubmit={handleSubmit}
        style={{
          display: "grid",
          gap: 16,
          background: "#fff",
          padding: 20,
          borderRadius: 12,
          boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
        }}
      >
        <div>
          <label>File</label>
          <br />
          <input
            type="file"
            accept=".csv,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </div>

        <div>
          <label>Template</label>
          <br />
          <select
            value={selectedTemplate}
            onChange={(e) => setSelectedTemplate(e.target.value)}
          >
            {templates.map((tpl) => (
              <option key={tpl.id} value={tpl.slug}>
                {tpl.name} ({tpl.slug})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Delimiter</label>
          <br />
          <select
            value={delimiter}
            onChange={(e) => setDelimiter(e.target.value as "comma" | "tab" | "space")}
          >
            <option value="comma">comma</option>
            <option value="tab">tab</option>
            <option value="space">space</option>
          </select>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              checked={hasHeader}
              onChange={(e) => setHasHeader(e.target.checked)}
            />{" "}
            Has Header
          </label>
        </div>

        <button
          type="submit"
          disabled={submitting}
          style={{
            padding: "10px 14px",
            borderRadius: 8,
            border: "none",
            background: "#111827",
            color: "#fff",
            cursor: "pointer"
          }}
        >
          {submitting ? "Creating..." : "Create Task"}
        </button>
      </form>
    </main>
  );
}
