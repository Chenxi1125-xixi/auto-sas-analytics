const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export type Template = {
  id: string;
  slug: string;
  name: string;
  description: string;
};

export type TaskListItem = {
  id: string;
  status: string;
  created_at: string;
};

export type TaskDetail = {
  id: string;
  status: string;
  uploaded_file_id: string;
  template_id: string;
  delimiter: string;
  has_header: boolean;
  params_json: Record<string, unknown>;
  artifacts: Record<string, string>;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
};

export type UploadResponse = {
  id: string;
  filename: string;
  file_type: string;
  storage_path: string;
};

export type RunTaskResponse = {
  id: string;
  status: string;
  artifacts: Record<string, string>;
  error_message?: string | null;
};

export async function getTemplates(): Promise<Template[]> {
  const res = await fetch(`${API_BASE}/api/templates`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load templates");
  return res.json();
}

export async function getTasks(): Promise<TaskListItem[]> {
  const res = await fetch(`${API_BASE}/api/tasks`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load tasks");
  return res.json();
}

export async function getTask(taskId: string): Promise<TaskDetail> {
  const res = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
    cache: "no-store"
  });
  if (!res.ok) throw new Error("Failed to load task");
  return res.json();
}

export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/uploads`, {
    method: "POST",
    body: formData
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Upload failed");
  }

  return res.json();
}

export async function createTask(payload: {
  uploaded_file_id: string;
  template_slug: string;
  delimiter: "comma" | "tab" | "space";
  has_header: boolean;
  params_json: Record<string, unknown>;
}): Promise<TaskDetail> {
  const res = await fetch(`${API_BASE}/api/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Create task failed");
  }

  return res.json();
}

export async function runTask(taskId: string): Promise<RunTaskResponse> {
  const res = await fetch(`${API_BASE}/api/tasks/${taskId}/run`, {
    method: "POST"
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Run task failed");
  }

  return res.json();
}

export async function getSystemCheck(): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/api/system/check`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load system check");
  return res.json();
}
